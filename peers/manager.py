from .peer import Peer
from struct import unpack
import socket
import logging
from asyncio import new_event_loop, coroutine
import asyncio
from threading import Thread
from .helpers import *
from .consts import *

class Manager():
    def __init__(self, ip, port):
        ip = socket.gethostbyname(ip)
        self.loop = new_event_loop()
        self.loop.set_debug(True)

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
        self.loop.run_until_complete(self._server_loop())

    @coroutine
    def _server_loop(self):
        self.socket.setblocking(0)
        while self.alive == True:
            clientsocket,addr = yield from self.loop.sock_accept(self.socket)
            self.log.info("Received a connection from {}".format(addr))
            clientsocket.setblocking(0)
            asyncio.ensure_future(self.handle_conn(clientsocket, addr), loop=self.loop)


    @coroutine
    def handle_conn(self, socket, addr):
        hi = yield from receive_hi(socket, self.loop)
        proto_v, ip, port, peer_id = hi

        assert proto_v == PROTO_VERSION

        yield from send_hi(socket, PROTO_VERSION, ip2int(self.ip), self.port, self.id, self.loop)

        self.log.info("Peer {} successfully handshaked".format(peer_id))

        peer = yield from self._add_peer(proto_v, int2ip(ip), port, peer_id, socket)
        return peer

    @coroutine
    def connect_to_peer(self, host, port):
        soc = socket.create_connection((host, port))
        soc.setblocking(0)
        yield from send_hi(soc, PROTO_VERSION, ip2int(self.ip), self.port, self.id, self.loop)
        hi = yield from receive_hi(soc, self.loop)

        proto_v, ip, port, peer_id = hi

        assert proto_v == PROTO_VERSION

        self.log.info("Peer {} successfully connected".format(peer_id))
        peer = yield from self._add_peer(proto_v, int2ip(ip), port, peer_id, soc)
        return peer

    @coroutine
    def _add_peer(self, proto_v, ip, port, peer_id, sock):
        if peer_id in self.peers:
            peer = peers[peer_id]
        else:
            peer = Peer(self, peer_id, proto_v, ip, port)
            self.peers[peer_id] = Peer
        yield from peer.receive_conn(sock)
        return peer

    def close(self):
        self.log.info("Shutting down")
        self.socket.close()
        self.alive = False
        self.log.info("Shut down successful")
