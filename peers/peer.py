import socket
import asyncio
from struct import pack

from .helpers import control_message
from .consts import *
from .asyncsocks import PeerAsync

class Peer():
    def __init__(self, manager, pid, proto_v, ip, port):
        self.manager = manager
        self.id = pid
        self.proto = proto_v
        self.ip = ip
        self.port = port

    async def receive_conn(self, sock):
        self.socket = sock
        loop = self.manager.loop
        transport, protocol = await loop.create_connection(lambda: PeerAsync(self), sock=sock)
        self.transport = transport
        # reader, writer = await asyncio.open_connection(sock=sock, loop = loop)
        self.reader = asyncio.StreamReader(loop=loop)
        self.writer = asyncio.StreamWriter(transport, protocol, self.reader, loop)
        # loop.add_reader(sock.fileno(), self.data_received)
        # asyncio.run_coroutine_threadsafe(connect_coro, loop)
        # transport, protocol = await connect_coro()

    async def send_raw_data(self, data):
        # loop = self.manager.loop
        # await loop.sock_sendall(self.socket, dat a)
        self.writer.write(data)
        await self.writer.drain()

    def data_received(self, data):
        print("Received data:" + str(data))

    def sync_meta(self):
        with socket.create_connection((self.ip, self.port)) as s:
            message = control_message((GET_STATE, 4))
            s.sendall(message)
            data = s.recv(1024)

    def get_headers(self):
        pass

