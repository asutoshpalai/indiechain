from struct import pack, unpack
from socket import inet_ntoa, inet_aton
from .consts import *
import random
import pickle
from Crypto.PublicKey import RSA

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

async def send_hi(socket, proto_v, role, ip, port, id, loop):
    data = pack(MSG_HI_FMT, START_STRING, MSG_HI, proto_v, role, ip, port, id)
    return await loop.sock_sendall(socket, data)

def get_headers_msg(known_header):
    return pack(MSG_GET_HEADER_FMT, START_STRING, MGS_GET_HEADER, known_header)

def generate_id():
    return random.getrandbits(64)

def data_serialize(header_fmt, obj_code, data):
    return pack(header_fmt, obj_code, len(data)) + data

def pickle_serialize(header_fmt, obj_code, obj):
    pick = pickle.dumps(obj)
    return data_serialize(header_fmt, obj_code, pick)

def trx_packet(transaction):
    return pack(">I", START_STRING) + pickle_serialize(TRX_HEADER_FMT, TRX_HEADER, transaction)

def miner_block_packet(block):
    return pack(">I", START_STRING) + pickle_serialize(MBLK_HEADER_FMT, MBLK_HEADER, block)

def block_packet(block):
    return pack(">I", START_STRING) + pickle_serialize(BLK_HEADER_FMT, BLK_HEADER, block)

def public_key_packet(key):
    return pack(">I", START_STRING) + data_serialize(PKEY_HEADER_FMT, PKEY_HEADER, key.exportKey())

def block_request_packet(hash):
    return pack(">I", START_STRING) + data_serialize(BLKR_HEADER_FMT, BLKR_HEADER, bytes(hash, 'ascii'))

def new_block_packet(block):
    return pack(">I", START_STRING) + pickle_serialize(BLKN_HEADER_FMT, BLKN_HEADER, block)

def miner_res_packet(res):
    return pack(">I", START_STRING) + pickle_serialize(MRES_HEADER_FMT, MRES_HEADER, res)

def deserialize_data(data, obj_type, header_len, header_fmt):
    header = data[:header_len]
    body = data[header_len:]
    h_type, l = unpack(header_fmt, header)
    assert h_type == obj_type
    assert len(body) == l

    return body

def deserialize_pickle(data, obj_type, header_len, header_fmt):
    body = deserialize_data(data, obj_type, header_len, header_fmt)
    return pickle.loads(body)

def deserialize_block(data):
    return deserialize_pickle(data, BLK_HEADER, BLK_HEADER_LENGTH, BLK_HEADER_FMT)

def deserialize_miner_block(data):
    return deserialize_pickle(data, MBLK_HEADER, MBLK_HEADER_LENGTH, MBLK_HEADER_FMT)

def deserialize_trx(data):
    return deserialize_pickle(data, TRX_HEADER, TRX_HEADER_LENGTH, TRX_HEADER_FMT)

def deserialize_public_key(data):
    return RSA.importKey(deserialize_data(data, PKEY_HEADER, PKEY_HEADER_LENGTH, PKEY_HEADER_FMT))

def deserialize_block_request(data):
    return deserialize_data(data, BLKR_HEADER, BLKR_HEADER_LENGTH, BLKR_HEADER_FMT).decode('ascii')

def deserialize_new_block(data):
    return deserialize_pickle(data, BLKN_HEADER, BLKN_HEADER_LENGTH, BLKN_HEADER_FMT)

def deserialize_miner_res(data):
    return deserialize_pickle(data, MRES_HEADER, MRES_HEADER_LENGTH, MRES_HEADER_FMT)


# ex: set tabstop=4 shiftwidth=4  expandtab:
