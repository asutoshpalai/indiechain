import socket
import asyncio
import logging
from struct import pack, unpack

from .helpers import *
from .consts import *

class Peer():
    def __init__(self, manager, pid, proto_v, role, ip, port):
        self.manager = manager
        self.id = pid
        self.proto = proto_v
        self.ip = ip
        self.port = port
        self.role = role
        self.log = logging.getLogger('Peer {} of {}'.format(self.id, manager.id))

        self._blk_wait = {}

    @asyncio.coroutine
    def receive_conn(self, sock):
        self.socket = sock
        self.log.debug("Connection created")
        self._add_sock_cb()

    def getPublicKey(self):
        return self._key

    def _add_sock_cb(self):
        loop = self.manager.loop
        loop.add_reader(self.socket.fileno(), self._data_cb)

    def _remove_sock_cb(self):
        loop = self.manager.loop
        loop.remove_reader(self.socket.fileno())

    def _data_cb(self):
        self.log.debug("Data recevied cb called")
        loop = self.manager.loop
        asyncio.ensure_future(self.recv_data(), loop=loop)

    @asyncio.coroutine
    def recv_data(self):
        loop = self.manager.loop
        self._remove_sock_cb()
        try:
            start = yield from loop.sock_recv(self.socket, 4)
            assert unpack(">I", start)[0] == START_STRING

            head = yield from loop.sock_recv(self.socket, MSG_HEADER_LENGTH)
            typ, size = unpack(MSG_HEADER_FMT, head)
            body = yield from loop.sock_recv(self.socket, size)
            yield from self.data_received(typ, head + body)
        finally:
            self._add_sock_cb()

    @asyncio.coroutine
    def send_raw_data_aysnc(self, data):
        loop = self.manager.loop
        self.log.debug("Sending raw data")
        yield from loop.sock_sendall(self.socket, data)
        self.log.debug("Sent raw data")

    @asyncio.coroutine
    def data_received(self, typ, data):
        if typ == TRX_HEADER:
            self.handleTransaction(data)
        elif typ == MBLK_HEADER:
            yield from self.handleMinerBlock(data)
        elif typ == BLK_HEADER:
            self.handleBlock(data)
        elif typ == PKEY_HEADER:
            self.receiveKey(data)
        elif typ == BLKR_HEADER:
            self.blockRequest(data)
        elif typ == BLKN_HEADER:
            self.receiveNewBlock(data)
        else:
            self.log.error("Unknown data type: " + hex(typ))

    def sync_meta(self):
        with socket.create_connection((self.ip, self.port)) as s:
            message = control_message((GET_STATE, 4))
            s.sendall(message)
            data = s.recv(1024)

    def get_headers(self):
        pass

    def send_data(self, data):
        loop = self.manager.loop
        if loop.is_running():
            asyncio.ensure_future(self.send_raw_data_aysnc(data), loop=self.manager.loop)
        else:
            loop.run_until_complete(self.send_raw_data_aysnc(data))

    def sendTransaction(self, transaction):
        """
        called by node on the same system to send the trx to the peer
        """
        trx = trx_packet(transaction)
        self.send_data(trx)

    def sendMinerBlock(self, block):
        """
        called by manager on the same system to send the block to the miners
        """
        blk = miner_block_packet(block)
        self.send_data(blk)

    def sendBlock(self, block):
        """
        called by manager on the same system to send the block to the peer
        """
        blk = block_packet(block)
        self.send_data(blk)

    @asyncio.coroutine
    def sendPublicKey(self):
        loop = self.manager.loop
        key = self.manager.node.getNodePublicKey()
        key = public_key_packet(key)
        self.send_data(key)

    def handleMinerBlock(self, data):
        block = deserialize_miner_block(data)
        yield from self.manager.receiveMinerBlock(block)

    def handleBlock(self, data):
        block = deserialize_block(data)
        self.manager.receiveBlock(block)

    def handleTransaction(self, data):
        trx = deserialize_trx(data)
        self.manager.receiveTransaction(trx)

    def receiveKey(self, data):
        self.log.debug("Received the public key")
        key = deserialize_public_key(data)
        self._key = key

    def blockRequest(self, data):
        hash = deserialize_block_request(data)
        self.log.info("Received block request: " + hash)
        block = self.manager.fetchNodeBlock(hash)

        # block.hash = hash # Remove this line - only for testing
        blk = new_block_packet(block)
        self.send_data(blk)

    def receiveNewBlock(self, data):
        block = deserialize_new_block(data)
        hash = block.hash
        self.log.info("Received block: " + hash)
        event = self._blk_wait[hash]
        self._blk_wait[hash] = block
        event.set()

    @asyncio.coroutine
    def fetchBlock(self, hash):
        if hash in self._blk_wait:
            obj = self._blk_wait[hash]

            # Request is already pending
            if type(obj) is not asyncio.Event:
                return obj

            event = obj
        else:
            blk_request = block_request_packet(hash)
            self.send_data(blk_request)
            event = asyncio.Event()
            self._blk_wait[hash] = event

        yield from event.wait()

        return self._blk_wait[hash]

# ex: set tabstop=4 shiftwidth=4  expandtab:
