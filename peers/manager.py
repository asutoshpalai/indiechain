from .peer import Peer
from struct import unpack
import socket
import logging
from asyncio import new_event_loop, coroutine, gather
import asyncio
from threading import Thread
from .helpers import *
from .consts import *

class Manager():
    def __init__(self, ip, port, id = False):
        ip = socket.gethostbyname(ip)
        self.loop = new_event_loop()
        self.loop.set_debug(True)

        self.ip = ip
        self.port = port

        if id:
            self.id = id
        else:
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

        self.node = False

    def setNode(self, node):
        self.node = node

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
        proto_v, role, ip, port, peer_id = hi

        assert proto_v == PROTO_VERSION

        role = bytes(self.node.ROLE, 'ascii')
        yield from send_hi(socket, PROTO_VERSION, role, ip2int(self.ip), self.port, self.id, self.loop)

        self.log.info("Peer {} successfully handshaked".format(peer_id))

        peer = yield from self._add_peer(proto_v, role.decode('ascii'), int2ip(ip), port, peer_id, socket)
        return peer

    @coroutine
    def connect_to_peer(self, host, port):
        soc = socket.create_connection((host, port))
        soc.setblocking(0)
        role = bytes(self.node.ROLE, 'ascii')
        yield from send_hi(soc, PROTO_VERSION, role, ip2int(self.ip), self.port, self.id, self.loop)
        hi = yield from receive_hi(soc, self.loop)

        proto_v, role, ip, port, peer_id = hi

        assert proto_v == PROTO_VERSION

        self.log.info("Peer {} successfully connected".format(peer_id))
        peer = yield from self._add_peer(proto_v, role.decode('ascii'), int2ip(ip), port, peer_id, soc)
        return peer

    @coroutine
    def _add_peer(self, proto_v, role, ip, port, peer_id, sock):
        if peer_id in self.peers:
            peer = peers[peer_id]
        else:
            peer = Peer(self, peer_id, proto_v, role, ip, port)
            asyncio.ensure_future(peer.sendPublicKey(), loop=self.loop)
            self.peers[peer_id] = peer
        yield from peer.receive_conn(sock)
        return peer

    def close(self):
        self.log.info("Shutting down")
        self.socket.close()
        self.alive = False
        self.log.info("Shut down successful")

    def receiveTransaction(self, trx):
        self.log.info("recevied transaction: " + repr(trx))

        if self.node:
            self.node.receiveTransaction(trx)

    @coroutine
    def receiveMinerBlock(self, block):
        self.log.info("recevied miner block: " + repr(block))

        if self.node:
            x = yield from self.node.evaluateBlock(block)
            return x

    def receiveBlock(self, block):
        self.log.info("recevied block: " + repr(block))

        if self.node:
            self.node.receiveBlock(block)

    def broadcastToMiners(self, block):
        self.log.info("broadcasting block to miners: " + repr(block))
        coros = [peer.sendMinerBlock(block) for id, peer in self.peers.items() if peer.role == 'M']
        f = gather(*coros, loop=self.loop)

        loop = self.loop
        if loop.is_running():
            future = asyncio.run_coroutine_threadsafe(f, loop)
            res =  future.result(30)
        else:
            res = loop.run_until_complete(f)

        return res


    # send block to peers
    def transmitToPeers(self, block):
        self.log.info("broadcasting block to peers: " + repr(block))
        [peer.sendBlock(block) for id, peer in self.peers.items()]

    # send transaction to peers
    def broadcastToPeers(self, trx):
        [peer.sendTransaction(trx) for id, peer in self.peers.items()]

    def getNodePublicKey(self, id):
        id = int(id, 16)
        return self.peers[id].getPublicKey()

    def getBlock(self, node_id, hash):
        node_id = int(node_id, 16)
        peer = self.peers[node_id]
        return peer.fetchBlock(hash)

    def fetchNodeBlock(self, hash):
        return self.node.chain.getBlock(hash)

# ex: set tabstop=4 shiftwidth=4  expandtab:
