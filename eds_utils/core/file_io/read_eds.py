'''Everything to read an eds/dcf file'''

import re
from datetime import datetime

from .. import DataType, ObjectType, AccessType, BAUD_RATE, str2int, StorageLocation
from ..eds import EDS, FileInfo, DeviceInfo, DeviceCommissioning
from ..objects import Variable, Array, Record

VARIABLE_ENTRIES = [
    'ParameterName',
    'Denotation',
    'ObjectType',
    ';StorageLocation',
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
    ';StorageLocation',
    'SubNumber',
]
'''All valid entries in an array and record'''


def read_eds(file_path: str) -> (EDS, list):
    '''
    Read a EDS/DCF file.

    Paramters
    ---------
    file_path: str
        Path to EDS/DCF file

    Returns
    -------
    EDS:
        The eds object.
    list:
        List of errors that occured when reading in the EDS/DCF.
    '''

    errors = []
    var = Variable()

    eds = EDS()
    errors = []

    with open(file_path, 'r') as fptr:
        raw = fptr.read()

    # check for CANopenNode eds/dcf
    for line in raw.split('\n'):
        if line.startswith(';StorageLocation'):
            eds.canopennode = True
            break

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

            # set subindex 0's storage_location
            eds[index][0].storage_location = eds[index].storage_location

            index = int(header[1:5], 16)
            subindex = int(header[8:-1], 16)

            if eds[index].storage_location != var.storage_location:
                errors.append(f'StorageLocation of [{index:X}] and {header} did not match')
                var.storage_location = eds[index].storage_location

            eds[index][subindex] = var
        elif header == '[FileInfo]':
            eds.file_info, err = _read_file_info(header, raw)
            errors += err
        elif header == '[DeviceInfo]':
            eds.device_info, err = _read_device_info(header, raw)
            errors += err
        elif header == '[DeviceComissioning]':  # only in DCFs, only one 'm' in header
            eds.device_commissioning, err = _read_device_commisioning(header, raw)
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
        else:
            errors.append(f'Unknown header: {header}')

    return eds, errors


def _read_variable(header: str, lines: dict, comments: str) -> (Variable, list):
    '''
    Read a variable section.

    Paramters
    ---------
    header: str
        The header for the section.
    lines: dict
        The entries for the section as dictionary.

    Returns
    -------
    Variable:
        The variable pulled from the section lines.
    list:
        List of errors that occured when reading in the section lines.
    '''

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

    if ';StorageLocation' in lines:  # optional, for CANopenNode support
        try:
            storage_location = lines[';StorageLocation']
            var.storage_location = StorageLocation[storage_location]
        except KeyError:
            errors.append(f'StorageLocation value of {storage_location} is invalid in {header}')

    for i in lines:
        if i not in VARIABLE_ENTRIES:
            errors.append(f'Unknown entry "{i}" in {header}')

    return var, errors


def _read_array(header: str, lines: dict, comments: str) -> (Array, list):
    '''
    Read a array section.

    Paramters
    ---------
    header: str
        The header for the section.
    lines: dict
        The entries for the section as dictionary.

    Returns
    -------
    Array:
        The array pulled from the section lines.
    list:
        List of errors that occured when reading in the section lines.
    '''

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

    if ';StorageLocation' in lines:  # optional, for CANopenNode support
        try:
            storage_location = lines[';StorageLocation']
            arr.storage_location = StorageLocation[storage_location]
        except KeyError:
            errors.append(f'StorageLocation value of {storage_location} is invalid in {header}')

    # NOTE: SubNumber is mandatory entry, but is not used by Array class

    for i in lines:
        if i not in ARRAY_RECORD_ENTRIES:
            errors.append(f'Unknown entry "{i}" in {header}')

    return arr, errors


def _read_record(header: str, lines: dict, comments: str) -> (Record, list):
    '''
    Read a record section.

    Paramters
    ---------
    header: str
        The header for the section.
    lines: dict
        The entries for the section as dictionary.

    Returns
    -------
    Record:
        The record pulled from the section lines.
    list:
        List of errors that occured when reading in the section lines.
    '''

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

    if ';StorageLocation' in lines:  # optional, for CANopenNode support
        try:
            storage_location = lines[';StorageLocation']
            rec.storage_location = StorageLocation[storage_location]
        except KeyError:
            errors.append(f'StorageLocation value of {storage_location} is invalid in {header}')

    # NOTE: SubNumber is mandatory entry, but is not used by Record class

    for i in lines:
        if i not in ARRAY_RECORD_ENTRIES:
            errors.append(f'Unknown entry "{i}" in {header}')

    return rec, errors


def _read_file_info(header: str, lines: dict) -> (FileInfo, list):
    '''
    Read the device info section.

    Paramters
    ---------
    header: str
        The header for the section.
    lines: dict
        The entries for the section as dictionary.

    Returns
    -------
    FileInfo:
        The file info pulled from the section lines.
    list:
        List of errors that occured when reading in the section lines.
    '''

    errors = []
    file_info = FileInfo()

    try:
        file_info.file_name = lines['FileName']
    except KeyError:
        errors.append(f'FileName was missing from {header}')

    try:
        file_info.file_version = _read_int_value(header, lines, 'FileVersion')
    except ValueError as exc:
        errors.append(str(exc))

    try:
        file_info.file_revision = _read_int_value(header, lines, 'FileRevision')
    except ValueError as exc:
        errors.append(str(exc))

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
        file_info.creation_dt = _read_datetime_value(header, lines, 'CreationTime',
                                                     'CreationDate')
    except ValueError as exc:
        errors.append(str(exc))

    try:
        file_info.created_by = lines['CreatedBy']
    except KeyError:
        errors.append(f'CreatedBy was missing from {header}')

    try:
        file_info.modification_dt = _read_datetime_value(header, lines, 'ModificationTime',
                                                         'ModificationDate')
    except ValueError as exc:
        errors.append(str(exc))

    try:
        file_info.modified_by = lines['ModifiedBy']
    except KeyError:
        errors.append(f'ModifiedBy was missing from {header}')

    return file_info, errors


def _read_device_info(header: str, lines: dict) -> (DeviceInfo, list):
    '''
    Read the device info section.

    Paramters
    ---------
    header: str
        The header for the section.
    lines: dict
        The entries for the section as dictionary.

    Returns
    -------
    DeviceInfo:
        The device info pulled from the section lines.
    list:
        List of errors that occured when reading in the section lines.
    '''

    errors = []
    device_info = DeviceInfo()

    try:
        device_info.vender_name = lines['VendorName']
    except KeyError:
        errors.append(f'VendorName was missing from {header}')

    try:
        device_info.vender_number = _read_int_value(header, lines, 'VendorNumber')
    except ValueError as exc:
        errors.append(str(exc))

    try:
        device_info.product_name = lines['ProductName']
    except KeyError:
        errors.append(f'ProductName was missing from {header}')

    try:
        device_info.product_number = _read_int_value(header, lines, 'ProductNumber')
    except ValueError as exc:
        errors.append(str(exc))

    try:
        device_info.revision_number = _read_int_value(header, lines, 'RevisionNumber')
    except ValueError as exc:
        errors.append(str(exc))

    try:
        device_info.order_code = lines['OrderCode']
    except KeyError:
        errors.append(f'OrderCode was missing from {header}')

    for i in BAUD_RATE:
        try:
            device_info.baud_rate[i] = _read_bool_value(header, lines, f'BaudRate_{i}')
        except ValueError as exc:
            errors.append(str(exc))

    try:
        device_info.simple_boot_up_master = _read_bool_value(header, lines,
                                                             'SimpleBootUpMaster')
    except ValueError as exc:
        errors.append(str(exc))

    try:
        device_info.simple_boot_up_slave = _read_bool_value(header, lines,
                                                            'SimpleBootUpSlave')
    except ValueError as exc:
        errors.append(str(exc))

    try:
        device_info.grandularity = _read_int_value(header, lines, 'Granularity')
    except ValueError as exc:
        errors.append(str(exc))

    try:
        device_info.dynamic_channel_supperted = _read_bool_value(header, lines,
                                                                 'DynamicChannelsSupported')
    except ValueError as exc:
        errors.append(str(exc))

    try:
        device_info.num_of_rpdo = _read_int_value(header, lines, 'NrOfRXPDO')
    except ValueError as exc:
        errors.append(str(exc))

    try:
        device_info.num_of_tpdo = _read_int_value(header, lines, 'NrOfTXPDO')
    except ValueError as exc:
        errors.append(str(exc))

    try:
        device_info.lss_supported = _read_bool_value(header, lines, 'LSS_Supported')
    except ValueError as exc:
        errors.append(str(exc))

    return device_info, errors


def _read_device_commisioning(header: str, lines: dict) -> (DeviceCommissioning, list):
    '''
    Read the device commissioning section.

    Paramters
    ---------
    header: str
        The header for the section.
    lines: dict
        The entries for the section as dictionary.

    Returns
    -------
    DeviceCommissioning:
        The device commissioning info pulled from the section lines.
    list:
        List of errors that occured when reading in the section lines.
    '''

    errors = []
    device_comm = DeviceCommissioning()

    try:
        device_comm.node_id = _read_int_value(header, lines, 'NodeID')
    except ValueError as exc:
        errors.append(str(exc))

    try:
        device_comm.node_name = lines['NodeName']
    except KeyError:
        errors.append(f'NodeName was missing from {header}')

    try:
        temp = _read_int_value(header, lines, 'Baudrate')
        if temp in BAUD_RATE:
            device_comm.baud_rate = temp
        else:
            errors.append(f'Baudrate in {header} was not a valid CANopen baud rate')
    except ValueError as exc:
        errors.append(str(exc))

    try:
        device_comm.net_number = _read_int_value(header, lines, 'NetNumber')
    except ValueError as exc:
        errors.append(str(exc))

    try:
        device_comm.network_name = lines['NetworkName']
    except KeyError:
        errors.append(f'NetworkName was missing from {header}')

    try:
        device_comm.canopen_manager = _read_bool_value(header, lines, 'CANopenManager')
    except ValueError as exc:
        errors.append(str(exc))

    try:
        device_comm.lss_serialnumber = _read_bool_value(header, lines, 'LSS_SerialNumber')
    except ValueError as exc:
        errors.append(str(exc))

    return device_comm, errors


def _read_bool_value(header: str, lines: dict, name: str) -> bool:
    '''
    Read the named value from the section and convert value to a boolean.

    Paramters
    ---------
    header: str
        The header for the section.
    lines: dict
        The entries for the section as dictionary.
    name: str
        The name of the int value.

    Raises
    ------
    ValueError:
        Values were mising or misformatted.

    Returns
    -------
    bool:
        The value as a bool.
    '''

    return bool(_read_int_value(header, lines, name))


def _read_int_value(header: str, lines: dict, name: str) -> int:
    '''
    Read the named value from the section and convert value to a integer.

    Paramters
    ---------
    header: str
        The header for the section.
    lines: dict
        The entries for the section as dictionary.
    name: str
        The name of the int value.

    Raises
    ------
    ValueError:
        Value were mising or misformatted.

    Returns
    -------
    int:
        The value as a int.
    '''

    try:
        temp = lines[name]
        value = str2int(temp)
    except KeyError:
        raise ValueError(f'{name} was missing from {header}')
    except ValueError:
        raise ValueError(f'{name} was incorrectly formatted in {header}')

    return value


def _read_datetime_value(header: str, lines: dict, time_name: str, date_name: str) -> datetime:
    '''
    Read the time and date values from the section and convert values to a `datetime` object.

    Paramters
    ---------
    header: str
        The header for the section.
    lines: dict
        The entries for the section as dictionary.
    time_name: str
        The name of the time value.
    time_name: str
        The name of the date value.

    Raises
    ------
    ValueError:
        Values were mising or misformatted.

    Returns
    -------
    datetime:
        The time and date values as a datetime object.
    '''

    try:
        time = lines[time_name]
        date = lines[date_name]
        value = datetime.now().strptime(f'{date} {time}', '%m-%d-%Y %I:%M%p')
    except KeyError:
        raise ValueError(f'{time_name} or {date_name} was missing from {header}')
    except ValueError:
        raise ValueError(f'{time_name} or {date_name} was incorrectly formatted in {header}')

    return value
