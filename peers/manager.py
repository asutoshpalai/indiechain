from .peer import Peer
from struct import unpack
import socket
import logging
from asyncio import new_event_loop, coroutine
from threading import Thread
from .helpers import *
from .consts import *

class Manager():
    def __init__(self, ip, port):
        ip = socket.gethostbyname(ip)
        self.loop = new_event_loop()

        self.ip = ip
        self.port = port
        self.id = generate_id()
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if ip == '127.0.0.1':
            serversocket.bind(('', port)) # listen for all connections
        else:
            serversocket.bind((ip, port))

        serversocket.listen(5)
        self.socket = serversocket
        self.peers = {}
        self.log = logging.getLogger('Peer Manager {}'.format(self.id))
        self.log.info("initialised at port {} with ip {}".format(port, ip))
        self.alive = True

    def activity_loop(self):
        Thread(target=lambda: self.loop.run_forever()).start()
        #self.loop.create_task(self._server_loop())
        #self.loop.run_forever()
        self._server_loop()

    # @coroutine
    def _server_loop(self):
        while True and self.alive == True:
            # clientsocket,addr = yield from self.loop.sock_accept(self.socket)
            clientsocket,addr = self.socket.accept()
            self.log.info("Received a connection from {}".format(addr))
            self.handle_conn(clientsocket, addr)


    def handle_conn(self, socket, addr):
        hi = receive_hi(socket)
        proto_v, ip, port, peer_id = hi

        assert proto_v == PROTO_VERSION

        send_hi(socket, PROTO_VERSION, ip2int(self.ip), self.port, self.id)

        self.log.info("Peer {} successfully handshaked".format(peer_id))

        return self._add_peer(proto_v, int2ip(ip), port, peer_id, socket)

    def connect_to_peer(self, host, port):
        soc = socket.create_connection((host, port))
        send_hi(soc, PROTO_VERSION, ip2int(self.ip), self.port, self.id)
        hi = receive_hi(soc)

        proto_v, ip, port, peer_id = hi

        assert proto_v == PROTO_VERSION

        self.log.info("Peer {} successfully connected".format(peer_id))
        return self._add_peer(proto_v, int2ip(ip), port, peer_id, soc)

    def _add_peer(self, proto_v, ip, port, peer_id, sock):
        if peer_id in self.peers:
            peer = peers[peer_id]
        else:
            peer = Peer(self, peer_id, proto_v, ip, port)
            self.peers[peer_id] = Peer
        peer.receive_conn(sock)
        return peer

    def close(self):
        self.log.info("Shutting down")
        self.socket.close()
        self.alive = False
        self.log.info("Shut down successful")
