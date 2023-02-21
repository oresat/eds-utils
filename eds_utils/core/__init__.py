import re
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

    @property
    def size(self):
        '''Get data size in bits (dynamic types like DOMAIN, VISIBLE_STRING, etc will return 0)'''
        size = 0

        if self.value in [DataType.BOOLEAN, DataType.INTEGER8, DataType.UNSIGNED8]:
            size = 8
        elif self.value in [DataType.INTEGER16, DataType.UNSIGNED16]:
            size = 16
        elif self.value in [DataType.INTEGER24, DataType.UNSIGNED24]:
            size = 24
        elif self.value in [DataType.INTEGER32, DataType.UNSIGNED32, DataType.REAL32]:
            size = 32
        elif self.value in [DataType.INTEGER40, DataType.UNSIGNED40]:
            size = 40
        elif self.value in [DataType.INTEGER48, DataType.UNSIGNED48, DataType.TIME_OF_DAY,
                            DataType.TIME_DIFFERENCE]:
            size = 48
        elif self.value in [DataType.INTEGER56, DataType.UNSIGNED56]:
            size = 56
        elif self.value in [DataType.INTEGER64, DataType.UNSIGNED64, DataType.REAL64]:
            size = 64

        return size


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


RPDO_TRANSMISSION_TYPES = []
for i in range(0, 0xF1):
    RPDO_TRANSMISSION_TYPES.append(f'Synchronous (0x{i:02X})')
for i in range(0xF1, 0xFE):
    RPDO_TRANSMISSION_TYPES.append(f'Reserved (0x{i:X})')
RPDO_TRANSMISSION_TYPES.append('Event-Driven (Manufacture)')
RPDO_TRANSMISSION_TYPES.append('Event-Driven (Device / App)')
'''All valid RPDO transmission types'''

TPDO_TRANSMISSION_TYPES = ['Synchronous (Acycle)']
TPDO_TRANSMISSION_TYPES.append('Synchronous every SYNC')
for i in range(2, 0xF1):
    TPDO_TRANSMISSION_TYPES.append(f'Synchronous every {i} SYNC')
for i in range(0xF1, 0xFC):
    TPDO_TRANSMISSION_TYPES.append(f'Reserved (0x{i:X})')
TPDO_TRANSMISSION_TYPES.append('RTC-only (Synchronous)')
TPDO_TRANSMISSION_TYPES.append('RTC-only (Event-Driven)')
TPDO_TRANSMISSION_TYPES.append('Event-Driven (Manufacture)')
TPDO_TRANSMISSION_TYPES.append('Event-Driven (Device / App)')
'''All valid TPDO transmission types'''


def pdo_mapping_fields(value: str) -> (int, int, int):
    '''
    Pull out the values from a PDO mapping value.

    Parameters
    ----------
    value: str
        The PDO mapping value

    Returns
    -------
    int
        Mapped object index
    int
        Mapped object subindex
    int
        Mapped object size in bits
    '''

    if not re.match(r'^0x[\da-zA-Z]{8}$', value):
        raise ValueError(f'Invalid pdo mapping value {value}')

    index = str2int(value[:6])
    subindex = str2int(f'0x{value[6:8]}')
    size = str2int(f'0x{value[8:]}')

    return index, subindex, size
