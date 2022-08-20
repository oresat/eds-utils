'''Everything to read an eds/dcf file'''

import re
from datetime import datetime

from .. import DataType, ObjectType, AccessType, BAUD_RATE
from ..eds import EDS, FileInfo, DeviceInfo
from ..objects import Variable, Array, Record

VARIABLE_ENTRIES = [
    'ParameterName',
    'Denotation',
    'ObjectType',
    'DataType',
    'LowLimit',
    'HighLimit',
    'DefaultValue',
    'AccessType',
    'PDOMapping',
]
'''All valid entries in an variable'''

ARRAY_RECORD_ENTRIES = [
    'ParameterName',
    'Denotation',
    'ObjectType',
    'SubNumber',
]
'''All valid entries in an array and record'''


def read_eds(file_path: str) -> (EDS, list):
    '''load an eds/dcf file'''

    eds = EDS()
    errors = []

    with open(file_path, 'r') as fptr:
        raw = fptr.read()

    for section_lines in raw.split('\n\n'):
        if section_lines == '':
            continue  # handle new line at EOF

        lines = section_lines.split('\n')
        header_index = [lines.index(i) for i in lines if i.startswith('[')][0]
        header = lines[header_index]

        comments = ''
        for i in lines[:header_index]:
            comments += i[1:] + '\n'
        comments = comments[:-1]  # remove trailing '\n'

        # read in all seciton entries/values
        raw = {}
        for i in lines[header_index + 1:]:
            if i == '':  # to handle eds with no trailing empty line
                continue
            entry, value = i.split('=')
            raw[entry] = value

        if re.match(r'^\[[0-9a-fA-F]{4}\]$', header):  # index
            if 'ObjectType' in raw:
                object_type = raw['ObjectType']
                object_type = ObjectType.from_str(object_type)
            else:  # if ObjectType is missing it is a VAR
                object_type = None

            if object_type in [None, ObjectType.VAR]:
                obj, err = _read_variable(header, raw, comments)
            elif object_type == ObjectType.ARRAY:
                obj, err = _read_array(header, raw, comments)
            elif object_type == ObjectType.RECORD:
                obj, err = _read_record(header, raw, comments)

            errors += err

            index = int(header[1:5], 16)

            eds[index] = obj
        elif re.match(r'^\[[0-9a-fA-F]{4}sub[0-9a-fA-F]{1,2}\]$', header):  # subindex
            var, err = _read_variable(header, raw, comments)

            errors += err

            # subindex 0 is the length of the array or record and must be a uint8
            if header.endswith('sub0]') and var.data_type != DataType.UNSIGNED8:
                errors.append(f'subindex 0 for {header} was not a UNSIGNED8')
                var.data_type = DataType.UNSIGNED8

            index = int(header[1:5], 16)
            subindex = int(header[8:-1], 16)

            eds[index][subindex] = var
        elif header == '[FileInfo]':
            eds.file_info, err = _read_file_info(header, raw)
            errors += err
        elif header == '[DeviceInfo]':
            eds.device_info, err = _read_device_info(header, raw)
            errors += err
        elif header == '[DummyUsage]':
            continue  # TODO
        elif header == '[Comments]':
            continue  # TODO
        elif header == '[MandatoryObjects]':
            continue  # TODO ?
        elif header == '[OptionalObjects]':
            continue  # TODO ?
        elif header == '[ManufacturerObjects]':
            continue  # TODO ?
        elif header == '[DeviceComissioning]':  # only in DCFs, only one 'm' in header
            continue  # TODO
        else:
            errors.append(f'Unknown header: {header}')

    return eds, errors


def _read_variable(header: str, lines: dict, comments: str) -> (Variable, list):
    errors = []
    var = Variable()
    var.comments = comments

    try:
        var.parameter_name = lines['ParameterName']
    except KeyError:
        errors.append(f'ParameterName was missing from {header}')

    if 'Denotation' in lines:
        var.denotation = lines['Denotation']

    try:
        data_type = lines['DataType']
        var.data_type = DataType.from_str(data_type)
    except KeyError:
        errors.append(f'DataType was missing from {header}')
    except ValueError:
        errors.append(f'DataType value of {data_type} is invalid in {header}')

    try:
        access_type = lines['AccessType']
        var.access_type = AccessType.from_str(access_type)
    except KeyError:
        errors.append(f'AccessType was missing from {header}')
    except ValueError:
        errors.append(f'AccessType value of {access_type} is invalid in {header}')

    if 'DefaultValue' in lines:  # optional
        var.default_value = lines['DefaultValue']

    try:
        pdo_mapping = lines['PDOMapping']
        var.pdo_mapping = bool(int(pdo_mapping))
    except KeyError:
        pass  # optional
    except ValueError:
        errors.append(f'PDOMapping value of {pdo_mapping} is invalid in {header}')

    if 'LowLimit' in lines:  # optional
        var.low_limit = lines['LowLimit']

    if 'HighLimit' in lines:  # optional
        var.high_limit = lines['HighLimit']

    for i in lines:
        if i not in VARIABLE_ENTRIES:
            errors.append(f'Unknown entry "{i}" in {header}')

    return var, errors


def _read_array(header: str, lines: dict, comments: str) -> (Array, list):
    errors = []
    arr = Array('')
    arr.comments = comments

    try:
        arr.parameter_name = lines['ParameterName']
    except KeyError:
        errors.append(f'ParameterName was missing from {header}')
        arr.parameter_name = 'Unknown array name'

    if 'Denotation' in lines:
        arr.denotation = lines['Denotation']

    # NOTE: SubNumber is mandatory entry, but is not used by Array class

    for i in lines:
        if i not in ARRAY_RECORD_ENTRIES:
            errors.append(f'Unknown entry "{i}" in {header}')

    return arr, errors


def _read_record(header: str, lines: dict, comments: str) -> (Record, list):
    errors = []
    rec = Record('')
    rec.comments = comments

    try:
        rec.parameter_name = lines['ParameterName']
    except KeyError:
        errors.append(f'ParameterName was missing from {header}')
        rec.parameter_name = 'Unknown record name'

    if 'Denotation' in lines:
        rec.denotation = lines['Denotation']

    # NOTE: SubNumber is mandatory entry, but is not used by Record class

    for i in lines:
        if i not in ARRAY_RECORD_ENTRIES:
            errors.append(f'Unknown entry "{i}" in {header}')

    return rec, errors


def _read_file_info(header: str, lines: dict) -> (FileInfo, list):
    errors = []
    file_info = FileInfo()

    try:
        file_info.file_name = lines['FileName']
    except KeyError:
        errors.append(f'FileName was missing from {header}')

    try:
        temp = lines['FileVersion']
        file_info.file_version = int(temp)
    except KeyError:
        errors.append(f'FileVersion was missing from {header}')
    except ValueError:
        errors.append(f'FileVersion was incorrectly formated in {header}')

    try:
        temp = lines['FileRevision']
        file_info.file_revision = int(temp)
    except KeyError:
        errors.append(f'FileRevision was missing from {header}')
    except ValueError:
        errors.append(f'FileRevision was incorrectly formated in {header}')

    try:
        file_info.eds_version = lines['EDSVersion']
    except KeyError:
        # optional, if missing it's v3.0
        file_info.eds_version = '3.0'

    try:
        file_info.description = lines['Description']
    except KeyError:
        errors.append(f'Description was missing from {header}')

    try:
        time = lines['CreationTime']
        date = lines['CreationDate']
        file_info.creation_dt = datetime.now().strptime(f'{date} {time}', '%m-%d-%Y %I:%M%p')
    except KeyError:
        errors.append(f'CreationTime or CreationDate was missing from {header}')
    except ValueError:
        errors.append(f'CreationTime or CreationDate was incorrectly formated in {header}')

    try:
        file_info.created_by = lines['CreatedBy']
    except KeyError:
        errors.append(f'CreatedBy was missing from {header}')

    try:
        time = lines['ModificationTime']
        date = lines['ModificationDate']
        file_info.modification_dt = datetime.now().strptime(f'{date} {time}', '%m-%d-%Y %I:%M%p')
    except KeyError:
        errors.append(f'ModificationTime or ModificationDate was missing from {header}')
    except ValueError:
        errors.append(f'ModificationTime or ModificationDate was incorrectly formated in {header}')

    try:
        file_info.modified_by = lines['ModifiedBy']
    except KeyError:
        errors.append(f'ModifiedBy was missing from {header}')

    return file_info, errors


def _read_device_info(header: str, lines: dict) -> (DeviceInfo, list):
    errors = []
    device_info = DeviceInfo()

    try:
        device_info.vender_name = lines['VendorName']
    except KeyError:
        errors.append(f'VendorName was missing from {header}')

    try:
        temp = lines['VendorNumber']
        device_info.vender_number = int(temp)
    except KeyError:
        errors.append(f'VendorNumber was missing from {header}')
    except ValueError:
        errors.append(f'VendorNumber was incorrectly formated in {header}')

    try:
        device_info.product_name = lines['ProductName']
    except KeyError:
        errors.append(f'ProductName was missing from {header}')

    try:
        temp = lines['ProductNumber']
        device_info.product_number = int(temp)
    except KeyError:
        errors.append(f'ProductNumber was missing from {header}')
    except ValueError:
        errors.append(f'ProductNumber was incorrectly formated in {header}')

    try:
        temp = lines['RevisionNumber']
        device_info.revision_number = int(temp)
    except KeyError:
        errors.append(f'RevisionNumber was missing from {header}')
    except ValueError:
        errors.append(f'RevisionNumber was incorrectly formated in {header}')

    try:
        device_info.order_code = lines['OrderCode']
    except KeyError:
        errors.append(f'OrderCode was missing from {header}')

    for i in BAUD_RATE:
        try:
            temp = lines[f'BaudRate_{i}']
            device_info.baud_rate[i] = bool(int(temp))
        except KeyError:
            errors.append(f'BaudRate_{i} was missing from {header}')
        except ValueError:
            errors.append(f'BaudRate_{i} was incorrectly formated in {header}')

    try:
        temp = lines['SimpleBootUpMaster']
        device_info.simple_boot_up_master = bool(int(temp))
    except KeyError:
        errors.append(f'SimpleBootUpMaster was missing from {header}')
    except ValueError:
        errors.append(f'SimpleBootUpMaster was incorrectly formated in {header}')

    try:
        temp = lines['SimpleBootUpSlave']
        device_info.simple_boot_up_slave = bool(int(temp))
    except KeyError:
        errors.append(f'SimpleBootUpSlave was missing from {header}')
    except ValueError:
        errors.append(f'SimpleBootUpSlave was incorrectly formated in {header}')

    try:
        temp = lines['Granularity']
        device_info.grandularity = int(temp)
    except KeyError:
        errors.append(f'Granularity was missing from {header}')
    except ValueError:
        errors.append(f'Granularity was incorrectly formated in {header}')

    try:
        temp = lines['DynamicChannelsSupported']
        device_info.dynamic_channel_supperted = bool(int(temp))
    except KeyError:
        errors.append(f'DynamicChannelsSupported was missing from {header}')
    except ValueError:
        errors.append(f'DynamicChannelsSupported was incorrectly formated in {header}')

    try:
        temp = lines['NrOfRXPDO']
        device_info.num_of_rpdo = int(temp)
    except KeyError:
        errors.append(f'NrOfRXPDO was missing from {header}')
    except ValueError:
        errors.append(f'NrOfRXPDO was incorrectly formated in {header}')

    try:
        temp = lines['NrOfTXPDO']
        device_info.num_of_tpdo = int(temp)
    except KeyError:
        errors.append(f'NrOfTXPDO was missing from {header}')
    except ValueError:
        errors.append(f'NrOfTXPDO was incorrectly formated in {header}')

    try:
        temp = lines['LSS_Supported']
        device_info.lss_supported = int(temp)
    except KeyError:
        errors.append(f'LSS_Supportedwas missing from {header}')
    except ValueError:
        errors.append(f'LSS_Supported was incorrectly formated in {header}')

    return device_info, errors
