from struct import pack, unpack
from socket import inet_ntoa, inet_aton
from .consts import *
import random

TYPE_MAP = {1: 'B', 2: 'H', 4: 'L', 8: 'Q'}

def create_message(*args):
    typed = [(x, '>' + TYPE_MAP(y)) for x, y in args]
    return ''.join([pack(y, x) for x, y in typed])

def control_message(*args):
    return create_message((CTRL_MESSAGE, 4), *args)

def ip2int(addr):
    return unpack("!I", inet_aton(addr))[0]

def int2ip(addr):
    return inet_ntoa(pack("!I", addr))

def receive_hi(socket):
    data = socket.recv(MSG_HI_LENGTH)
    hi = unpack(MSG_HI_FMT, data)
    return hi[1:] # remove the msg type

def send_hi(socket, proto_v, ip, port, id):
    data = pack(MSG_HI_FMT, MSG_HI, proto_v, ip, port, id)
    return socket.send(data)

def generate_id():
    return random.getrandbits(64)

