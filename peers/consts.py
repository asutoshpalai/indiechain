from struct import calcsize
GET_STATE = 0x00000001
PEER_ID_LENGHT = 8

PROTO_VERSION = 0x00000001

MSG_HI = 0x00000000
#MSG type # Proto version # IP Addr #port #id
MSG_HI_FMT = ">IIIHQ"
MSG_HI_LENGTH = calcsize(MSG_HI_FMT)
