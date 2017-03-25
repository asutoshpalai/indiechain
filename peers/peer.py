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

    def receive_conn(self, sock):
        self.socket = sock
        loop = self.manager.loop
        connect_coro = loop.create_connection(lambda: PeerAsync(self), sock=sock)
        print(connect_coro)
        # loop.run_until_complete(connect_coro)
        # loop.call_soon(connect_coro)
        # print(dir(loop))
        # loop.run_in_executor(connect_coro)
        # asyncio.ensure_future(connect_coro, loop=loop)
        # asyncio.async(connect_coro, loop=loop)
        asyncio.run_coroutine_threadsafe(connect_coro, loop)

    def _add_to_async_listen(self, sock):
        pass

    def send_raw_data(self, data):
        return self.socket.sendall(data)

    def data_received(self, data):
        print("Received data:" + str(data))

    def sync_meta(self):
        with socket.create_connection((self.ip, self.port)) as s:
            message = control_message((GET_STATE, 4))
            s.sendall(message)
            data = s.recv(1024)
