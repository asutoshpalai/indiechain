import socket
import asyncio
import logging
from struct import pack

from .helpers import control_message
from .consts import *

class Peer():
    def __init__(self, manager, pid, proto_v, ip, port):
        self.manager = manager
        self.id = pid
        self.proto = proto_v
        self.ip = ip
        self.port = port
        self.log = logging.getLogger('Peer {} of {}'.format(self.id, manager.id))

    @asyncio.coroutine
    def receive_conn(self, sock):
        self.socket = sock
        loop = self.manager.loop
        loop.add_reader(sock.fileno(), self._data_cb)
        self.log.debug("Connection created")

    def _data_cb(self):
        self.log.debug("Data recevied cb called")
        data = self.socket.recv(1024)
        self.data_received(data)


    @asyncio.coroutine
    def send_raw_data(self, data):
        loop = self.manager.loop
        self.log.debug("Sending raw data")
        yield from loop.sock_sendall(self.socket, data)
        self.log.debug("Sent raw data")

    def data_received(self, data):
        print("Received data:" + str(data))

    def sync_meta(self):
        with socket.create_connection((self.ip, self.port)) as s:
            message = control_message((GET_STATE, 4))
            s.sendall(message)
            data = s.recv(1024)

    def get_headers(self):
        pass

