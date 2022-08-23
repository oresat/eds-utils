from enum import Enum, IntEnum, auto


BAUD_RATE = [
    10,
    20,
    50,
    125,
    250,
    500,
    800,
    1000,
]
'''CANopen baud rates in kpbs'''


def str2int(value: str) -> int:
    '''Convert str from eds files to int. Support base 10 and 16 definitions.'''

    if value.startswith('0x'):
        ret = int(value, 16)
    else:
        ret = int(value)

    return ret


class ObjectType(IntEnum):
    VAR = 0x07
    ARRAY = 0x08
    RECORD = 0x09

    @staticmethod
    def from_str(value: str):
        return ObjectType(str2int(value))

    def to_str(self):
        return f'0x{self.value:02X}'


class DataType(IntEnum):
    BOOLEAN = 0x0001
    INTEGER8 = 0x0002
    INTEGER16 = 0x0003
    INTEGER32 = 0x0004
    UNSIGNED8 = 0x0005
    UNSIGNED16 = 0x0006
    UNSIGNED32 = 0x0007
    REAL32 = 0x0008
    VISIBLE_STRING = 0x0009
    OCTET_STRING = 0x000A
    UNICODE_STRING = 0x000B
    TIME_OF_DAY = 0x000C
    TIME_DIFFERENCE = 0x000D
    # 0x000E reserved
    DOMAIN = 0x000F
    INTEGER24 = 0x0010
    REAL64 = 0x0011
    INTEGER40 = 0x0012
    INTEGER48 = 0x0013
    INTEGER56 = 0x0014
    INTEGER64 = 0x0015
    UNSIGNED24 = 0x0016
    # 0x0017 reserved
    UNSIGNED40 = 0x0018
    UNSIGNED48 = 0x0019
    UNSIGNED56 = 0x001A
    UNSIGNED64 = 0x001B

    @staticmethod
    def from_str(value: str):
        return DataType(str2int(value))

    def to_str(self):
        return f'0x{self.value:04X}'


class AccessType(Enum):
    RO = auto()
    WO = auto()
    RW = auto()
    RWR = auto()
    RWW = auto()
    CONST = auto()

    @staticmethod
    def from_str(value: str):
        return AccessType[value.upper()]

    def to_str(self):
        return self.name.lower()


class StorageLocation(Enum):
    '''for CANopenNode support'''
    RAM = auto()
    ROM = auto()
    PERSIST_COMM = auto()
    PERSIST_MFR = auto()
