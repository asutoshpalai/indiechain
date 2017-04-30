import socket
import asyncio
import logging
from struct import pack, unpack

from .helpers import control_message, trx_packet, deserialize_trx
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

    @asyncio.coroutine
    def receive_conn(self, sock):
        self.socket = sock
        self.log.debug("Connection created")
        self._add_sock_cb()

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

    def recv_data(self):
        loop = self.manager.loop
        self._remove_sock_cb()
        try:
            start = yield from loop.sock_recv(self.socket, 4)
            assert unpack(">I", start)[0] == START_STRING

            head = yield from loop.sock_recv(self.socket, MSG_HEADER_LENGTH)
            typ, size = unpack(MSG_HEADER_FMT, head)
            body = yield from loop.sock_recv(self.socket, size)
            self.data_received(typ, head + body)
        finally:
            self._add_sock_cb()

    @asyncio.coroutine
    def send_raw_data_aysnc(self, data):
        loop = self.manager.loop
        self.log.debug("Sending raw data")
        yield from loop.sock_sendall(self.socket, data)
        self.log.debug("Sent raw data")

    def data_received(self, typ, data):
        if typ == TRX_HEADER:
            self.handleTransaction(data)
        else:
            self.log.error("Unknown data type: " + str(typ))

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

    def receiveTransaction(self, transaction):
        """
        called by node on the same system to send the trx to the peer
        """
        trx = trx_packet(transaction)
        self.send_data(trx)

    def handleTransaction(self, data):
        trx = deserialize_trx(data)
        self.manager.receiveTransaction(trx)
