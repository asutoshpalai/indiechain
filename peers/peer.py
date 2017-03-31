import socket
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

    def receive_conn(self, socket):
        self.socket = socket

    def sync_meta(self):
        with socket.create_connection((self.ip, self.port)) as s:
            message = control_message((GET_STATE, 4))
            s.sendall(message)
            data = s.recv(1024)
