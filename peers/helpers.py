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

async def receive_hi(socket, loop):
    data = await loop.sock_recv(socket, MSG_HI_LENGTH)
    hi = unpack(MSG_HI_FMT, data)
    return hi[2:] # remove the start and the msg type

async def send_hi(socket, proto_v, ip, port, id, loop):
    data = pack(MSG_HI_FMT, START_STRING, MSG_HI, proto_v, ip, port, id)
    return await loop.sock_sendall(socket, data)

def get_headers_msg(known_header):
    return pack(MSG_GET_HEADER_FMT, START_STRING, MGS_GET_HEADER, known_header)

def generate_id():
    return random.getrandbits(64)