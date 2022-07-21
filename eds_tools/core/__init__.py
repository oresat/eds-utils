from enum import IntEnum


class ObjectType(IntEnum):
    VAR = 0x07
    ARRAY = 0x08
    RECORD = 0x09


class DataType(IntEnum):
    BOOLEAN = 0x01
    INTEGER8 = 0x02
    INTEGER16 = 0x03
    INTEGER32 = 0x04
    UNSIGNED8 = 0x05
    UNSIGNED16 = 0x06
    UNSIGNED32 = 0x07
    REAL32 = 0x08
    VISIBLE_STRING = 0x09
    OCTET_STRING = 0x0A
    UNICODE_STRING = 0x0B
    TIME_OF_DAY = 0x0C
    TIME_DIFFERENCE = 0x0D
    # 0x0E reserved
    DOMAIN = 0x0F
    INTEGER24 = 0x10
    REAL64 = 0x11
    INTEGER40 = 0x12
    INTEGER48 = 0x13
    INTEGER56 = 0x14
    INTEGER64 = 0x15
    UNSIGNED24 = 0x16
    # 0x17 reserved
    UNSIGNED40 = 0x18
    UNSIGNED48 = 0x19
    UNSIGNED56 = 0x1A
    UNSIGNED64 = 0x1B


BAUD_RATE = [
    10,
    50,
    100,
    125,
    250,
    500,
    800,
    1000,
]

ACCESS_TYPE = [
    'ro',
    'wo',
    'rw',
    'rwr',
    'rww',
    'const',
]


def str2int(string: str) -> int:
    '''definition strait from CiA 306'''

    if string.startswith('0x'):
        ret = int(string, 16)
    else:
        ret = int(string)

    return ret
