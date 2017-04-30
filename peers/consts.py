from struct import calcsize
GET_STATE = 0x00000001
PEER_ID_LENGHT = 8

START_STRING = 0x0b110907
PROTO_VERSION = 0x00000001

MSG_HI = 0x00000000
# start string #MSG type # Proto version # Role # IP Addr #port #id
MSG_HI_FMT = ">IIIcIHQ"
MSG_HI_LENGTH = calcsize(MSG_HI_FMT)

MSG_HEADER_FMT = ">II"
MSG_HEADER_LENGTH = calcsize(MSG_HEADER_FMT)

TRX_HEADER = 0x10000001
# obj_type, pickle length
TRX_HEADER_FMT = MSG_HEADER_FMT
TRX_HEADER_LENGTH = calcsize(TRX_HEADER_FMT)
