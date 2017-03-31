import socket
import asyncio
import logging
from struct import pack

from .helpers import control_message
from .consts import *
from .asyncsocks import PeerStreamReader

class Peer():
    def __init__(self, manager, pid, proto_v, ip, port):
        self.manager = manager
        self.id = pid
        self.proto = proto_v
        self.ip = ip
        self.port = port
        self.log = logging.getLogger('Peer {} of {}'.format(self.id, manager.id))

    async def receive_conn(self, sock):
        self.socket = sock
        loop = self.manager.loop
        # loop.add_reader(sock.fileno(), self._data_cb)
        reader, writer = await asyncio.open_connection(sock=sock, loop=loop)
        # reader = PeerStreamReader(self._data_cb, loop=loop)
        # protocol = asyncio.StreamReaderProtocol(reader, loop=loop)
        # transport, _ = await loop.create_connection(lambda: protocol, sock=sock)
        # writer = asyncio.StreamWriter(transport, protocol, reader, loop)
        # self.reader = reader
        # self.writer = writer
        self.log.debug("Connection created")
        data = await reader.read(1024)
        print("data received" + str(data))

    def _data_cb(self):
        self.log.debug("Data recevied cb called")
        data = self.reader.read(1024)
        self.data_received(data)


    async def send_raw_data(self, data):
        # loop = self.manager.loop
        # await loop.sock_sendall(self.socket, dat a)
        self.writer.write(data)
        await self.writer.drain()
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

