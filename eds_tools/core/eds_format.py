import re
from datetime import datetime

from . import ObjectType, DataType, str2int

INDEX_REGEX = r'^[0-9a-fA-F]{4}$'

SUBINDEX_REGEX = r'^[0-9a-fA-F]{4}sub[0-9a-fA-F]{1,2}$'

MANDATORY_OBJECTS = ['0x1000', '0x1001', '0x1018']


class EDSValue:
    def __init__(self, description='', default=None, optional=False):
        self.description = description
        self.default = default
        self.optional = optional

    def str2value(self, string: str) -> str:
        return string

    def value2str(self, value: str) -> str:
        return value

    def is_valid(self, value) -> bool:
        return True


class EDSString(EDSValue):
    def __init__(self, description='', default='', optional=False, max_length=0, regex_format=r''):
        super().__init__(description, default, optional)
        self.max_length = max_length
        self.regex_format = regex_format

    def is_valid(self, value: str) -> bool:
        if (not self.regex_format or re.match(self.regex_format, value)) and \
                (self.max_length == 0 or len(value) <= self.max_length):
            return True
        return False

    def str2value(self, string: str) -> str:
        if not self.is_valid(string):
            raise ValueError('invalid string format')
        return string

    def value2str(self, value: str) -> str:
        if not self.is_valid(value):
            raise ValueError('invalid string format')
        return value


class EDSInt(EDSValue):
    def __init__(self, description='', default=0, optional=False, min_value=None, max_value=None):
        super().__init__(description, default, optional)
        self.min: int = min_value
        self.max: int = max_value

    def str2value(self, string: str) -> int:
        return int(string)

    def value2str(self, value: int) -> str:
        return str(value)

    def is_valid(self, value: int) -> bool:
        if (not self.min and value < self.min) or (not self.max and value > self.max):
            return False
        return True


class EDSBool(EDSValue):
    def __init__(self, description='', default=False, optional=False):
        super().__init__(description, default, optional)

    def str2value(self, string: str) -> bool:
        return bool(int(string))

    def value2str(self, value: bool) -> str:
        return str(int(value))


class EDSObjectType(EDSValue):
    def __init__(self, description='', default=ObjectType.VAR, optional=False):
        super().__init__(description, default, optional)

    def str2value(self, string: str) -> ObjectType:
        return ObjectType(str2int(string))

    def value2str(self, value: ObjectType) -> str:
        return hex(value.value)


class EDSDataType(EDSValue):
    def __init__(self, description='', default=DataType.INTEGER32, optional=False):
        super().__init__(description, default, optional)

    def str2value(self, string: str) -> DataType:
        return DataType(str2int(string))

    def value2str(self, value: DataType) -> str:
        return '0x{0:0{1}X}'.format(value.value, 4)  # 0xABCD format (4 digits)


FILE_INFO = {
    'FileName': EDSString(max_length=243),
    'FileVersion': EDSInt(min_value=0, max_value=255),
    'FileRevision': EDSInt(min_value=0, max_value=255),
    'EDSVersion': EDSString(
        description='the version of EDS in  X.Y format',
        default='4.0',
        optional=True,
        regex_format=r'^\d\.\d$'
    ),
    'Description': EDSString(
        description='file description',
        max_length=243
    ),
    'CreationTime': EDSString(
        description='Time when the file was made in hh:mm(AM|PM) format',
        default=datetime.now().strftime('%I:%M%p'),
        regex_format=r'^([0-1]\d):([0-5]\d)(AM|PM)$'
    ),
    'CreationDate': EDSString(
        description='Date when the file was made in dd-mm-yyyy format',
        default=datetime.now().strftime('%m-%d-%Y'),
        regex_format=r'^(\d\d)-(\d\d)-(\d\d\d\d)$'
    ),
    'CreatedBy': EDSString(max_length=245),
    'ModificationTime': EDSString(
        description='Time when the file was made in hh:mm(AM|PM) format',
        default=datetime.now().strftime('%I:%M%p'),
        regex_format=r'^([0-1]\d):([0-5]\d)(AM|PM)$'
    ),
    'ModificationDate': EDSString(
        description='Date when the file was made in dd-mm-yyyy format',
        default=datetime.now().strftime('%m-%d-%Y'),
        regex_format=r'^(\d\d)-(\d\d)-(\d\d\d\d)$'
    ),
    'ModifiedBy': EDSString(max_length=244),
}

DEVICE_INFO = {
    'VendorName': EDSString(max_length=244),
    'VendorNumber': EDSInt(min_value=0, max_value=0xFFFFFFFF),
    'ProductName': EDSString(max_length=243),
    'ProductNumber': EDSInt(min_value=0, max_value=0xFFFFFFFF),
    'RevisionNumber': EDSInt(min_value=0, max_value=0xFFFFFFFF),
    'OrderCode': EDSString(description='order code for this product', max_length=245),
    'BaudRate_10': EDSBool(description='Supports baud rate of 20', default=True),
    'BaudRate_20': EDSBool(description='Supports baud rate of 20', default=True),
    'BaudRate_50': EDSBool(description='Supports baud rate of 50', default=True),
    'BaudRate_125': EDSBool(description='Supports baud rate of 125', default=True),
    'BaudRate_250': EDSBool(description='Supports baud rate of 250', default=True),
    'BaudRate_500': EDSBool(description='Supports baud rate of 500', default=True),
    'BaudRate_800': EDSBool(description='Supports baud rate of 800', default=True),
    'BaudRate_1000': EDSBool(description='Supports baud rate of 1000', default=True),
    'SimpleBootUpMaster': EDSBool(),
    'SimpleBootUpSlave': EDSBool(),
    'Granularity': EDSInt(
        description='granularity of PDO mapping',
        default=8,
        min_value=0,
        max_value=64
    ),
    'DynamicChannelsSupported': EDSBool(),
    'GroupMessaging': EDSBool(),
    'NrOfRXPDO': EDSInt(min_value=0, max_value=0xFFFF),
    'NrOfTXPDO': EDSInt(min_value=0, max_value=0xFFFF),
    'LSS_Supported': EDSBool(),
}

DEVICE_COMMISSIONING = {
    'NodeID': EDSInt(default=0x1, min_value=0x1, max_value=0xFF),
    'NodeName': EDSString(max_length=246),
    'Baudrate': EDSInt(default=1000, min_value=10, max_value=1000),
    'NetNumber': EDSInt(default=0, min_value=0, max_value=0xFFFFFFFF),
    'NetworkName': EDSString(max_length=243),
    'CANopenManager': EDSBool(default=False, optional=True),
    'LSS_SerialNumber': EDSInt(default=0, min_value=0, max_value=0xFFFFFFFF),
}

DUMMY_USAGE = {
    'Dummy0001': EDSBool(default=False),
    'Dummy0002': EDSBool(default=True),
    'Dummy0003': EDSBool(default=True),
    'Dummy0004': EDSBool(default=True),
    'Dummy0005': EDSBool(default=True),
    'Dummy0006': EDSBool(default=True),
    'Dummy0007': EDSBool(default=True),
}

RECORD_ARRAY = {
    'SubNumber': EDSString(),
    'ParameterName': EDSString(max_length=241),
    'Denotation': EDSString(),
    'ObjectType': EDSObjectType(),
}

VAR = {
    'ParameterName': EDSString(max_length=241),
    'Denotation': EDSString(),
    'ObjectType': EDSObjectType(),
    'DataType': EDSDataType(),
    'LowLimit': EDSString(optional=True),
    'HighLimit': EDSString(optional=True),
    'AccessType': EDSString(default='rw'),
    'DefaultValue': EDSString(),
    'PDOMapping': EDSBool(),
}

LIST_OBJECTS = {
    'SupportedObjects': EDSInt(min_value=1),
}

COMMENTS = {
    'Lines': EDSInt(min_value=0),
}

EDS_SECTION_ORDER = {
    'FileInfo': FILE_INFO,
    'DeviceInfo': DEVICE_INFO,
    'DeviceComissioning': DEVICE_COMMISSIONING,  # only in DCFS, one 'm' in header
    'DummyUsage': DUMMY_USAGE,
    'Comments': COMMENTS,
    'MandatoryObjects': LIST_OBJECTS,
    'OptionalObjects': LIST_OBJECTS,
    'ManufacturerObjects': LIST_OBJECTS,
}
