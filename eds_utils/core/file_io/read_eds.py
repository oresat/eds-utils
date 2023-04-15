'''Everything to read an eds/dcf file'''

import re
from datetime import datetime

from .. import DataType, ObjectType, AccessType, BAUD_RATE, str2int, pdo_mapping_fields
from ..eds import EDS, FileInfo, DeviceInfo, DeviceCommissioning
from ..objects import Variable, Array, Record

VARIABLE_ENTRIES = [
    'ParameterName',
    'Denotation',
    'ObjectType',
    ';StorageLocation',  # CANopenNode support
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
    ';StorageLocation',  # CANopenNode support
    'SubNumber',
]
'''All valid entries in an array and record'''

_LEVEL = 'AUTO-FIXED'


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

    mandatory_objs = []
    manufacturer_objs = []
    optional_objs = []

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

            sl = obj.storage_location
            if sl not in eds.storage_locations and sl != '':
                eds.add_storage_location(sl)

            errors += err

            index = int(header[1:5], 16)

            eds[index] = obj
        elif re.match(r'^\[[0-9a-fA-F]{4}sub[0-9a-fA-F]{1,2}\]$', header):  # subindex
            var, err = _read_variable(header, raw, comments)

            errors += err

            # subindex 0 is the length of the array or record and must be a uint8
            if header.endswith('sub0]') and var.data_type != DataType.UNSIGNED8:
                errors.append(f'{_LEVEL}: subindex 0 for {header} was not a UNSIGNED8')
                var.data_type = DataType.UNSIGNED8

            # set subindex 0's storage_location
            sl = eds[index].storage_location
            if eds[index][0].storage_location == '':
                eds[index][0].storage_location = sl

            if sl not in eds.storage_locations and sl != '':
                eds.add_storage_location(sl)

            index = int(header[1:5], 16)
            subindex = int(header[8:-1], 16)

            if eds[index].storage_location != var.storage_location:
                errors.append(f'{_LEVEL}: StorageLocation of [{index:X}] and {header} did not '
                              'match')
                var.storage_location = eds[index].storage_location

            eds[index][subindex] = var
        elif header == '[FileInfo]':
            eds.file_info, err = _read_file_info(header, raw)
            errors += err
        elif header == '[DeviceInfo]':
            eds.device_info, err = _read_device_info(header, raw)
            errors += err
        elif header == '[DeviceComissioning]':  # only in DCFs, only one 'm' in header
            eds.device_commissioning, err = _read_device_commissioning(header, raw)
            errors += err
        elif header == '[DummyUsage]':
            continue  # TODO
        elif header == '[Comments]':
            continue  # TODO
        elif header == '[MandatoryObjects]':
            keys = list(raw.keys())
            keys.remove('SupportedObjects')
            mandatory_objs = [str2int(raw[i]) for i in keys]
        elif header == '[OptionalObjects]':
            keys = list(raw.keys())
            keys.remove('SupportedObjects')
            optional_objs = [str2int(raw[i]) for i in keys]
        elif header == '[ManufacturerObjects]':
            keys = list(raw.keys())
            keys.remove('SupportedObjects')
            manufacturer_objs = [str2int(raw[i]) for i in keys]
        else:
            errors.append(f'{_LEVEL}: Unknown header: {header}')

    if mandatory_objs:
        a = set(mandatory_objs)
        b = set(eds.mandatory_objects)
        for i in list(a - b):
            errors.append(f'{_LEVEL}: 0x{i:X} was missing from [MandatoryObjects]')
        for i in list(b - a):
            errors.append(f'{_LEVEL}: 0x{i:X} was in [MandatoryObjects], but does not exist')
    else:
        errors.append(f'{_LEVEL}: Section [MandatoryObjects] was missing')

    if optional_objs:
        a = set(optional_objs)
        b = set(eds.optional_objects)
        for i in list(a - b):
            errors.append(f'{_LEVEL}: 0x{i:X} was missing from [OptionalObjects]')
        for i in list(b - a):
            errors.append(f'{_LEVEL}: 0x{i:X} was in [OptionalObjects], but does not exist')
    else:
        errors.append(f'{_LEVEL}: Section [OptionalObjects] was missing')

    if manufacturer_objs:
        a = set(manufacturer_objs)
        b = set(eds.manufacturer_objects)
        for i in list(a - b):
            errors.append(f'{_LEVEL}: 0x{i:X} was missing from [ManufacturerObjects]')
        for i in list(b - a):
            errors.append(f'{_LEVEL}: 0x{i:X} was in [ManufacturerObjects], but does not exist')
    else:
        errors.append(f'{_LEVEL}: Section [ManufacturerObjects] was missing')

    rpdo_para_ind = [i for i in eds.indexes if i >= EDS.RPDO_PARA_START and i < EDS.RPDO_PARA_END]
    tpdo_para_ind = [i for i in eds.indexes if i >= EDS.TPDO_PARA_START and i < EDS.TPDO_PARA_END]

    for i in rpdo_para_ind + tpdo_para_ind:

        if i < EDS.TPDO_PARA_START:
            pdo = f'RPDO {i - EDS.RPDO_PARA_START}'
        else:
            pdo = f'TPDO {i - EDS.TPDO_PARA_START}'

        for j in eds[i].subindexes:
            if j == 0:
                continue

            try:
                obj_index, obj_subindex, obj_size = pdo_mapping_fields(eds[i][j].default_value)
            except ValueError:
                errors.append(f'{_LEVEL}: {pdo} mapping value at subindex 0x{j:02X} was '
                              f'misformatted, replacing {eds[i][j].default_value} with 0x00000000')
                eds[i][j].default_value = '0x00000000'
                continue

            if obj_index == 0 and obj_subindex == 0 and obj_size == 0:
                continue

            if isinstance(eds[obj_index], Variable):
                obj = eds[obj_index]
            else:
                obj = eds[obj_index][obj_subindex]

            if obj.data_type.size != obj_size:
                map_obj = eds[i][j]
                old = map_obj.default_value
                map_obj.default_value = map_obj.default_value[:-2] + f'{obj.data_type.size:02X}'
                new = map_obj.default_value

                errors.append(f'{_LEVEL}: {pdo} mapping value at subindex 0x{j:02X} had the wrong '
                              f'mapped object size: {old} -> {new}')

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
        errors.append(f'{_LEVEL}: ParameterName was missing from {header}')

    if 'Denotation' in lines:
        var.denotation = lines['Denotation']

    try:
        data_type = lines['DataType']
        var.data_type = DataType.from_str(data_type)
    except KeyError:
        errors.append(f'{_LEVEL}: DataType was missing from {header}')
    except ValueError:
        errors.append(f'{_LEVEL}: DataType value of {data_type} is invalid in {header}')

    try:
        access_type = lines['AccessType']
        var.access_type = AccessType.from_str(access_type)
    except KeyError:
        errors.append(f'{_LEVEL}: AccessType was missing from {header}')
    except ValueError:
        errors.append(f'{_LEVEL}: AccessType value of {access_type} is invalid in {header}')

    list_data_types = [DataType.VISIBLE_STRING, DataType.OCTET_STRING, DataType.UNICODE_STRING,
                       DataType.DOMAIN]

    if 'DefaultValue' in lines:  # optional
        if var.data_type == DataType.OCTET_STRING:
            value = lines['DefaultValue']
            value_ns = value.replace(' ', '')

            # format OCTET_STRING's default value
            if re.match(r'^([\da-fA-F]{2} *)*$', value):
                tmp = [value_ns[i: i + 2] for i in range(0, len(value_ns), 2)]
                var.default_value = ' '.join(tmp)
            else:
                errors.append(f'Octect\'s DefaultValue value of {value} is invalid in {header}')
        else:
            var.default_value = lines['DefaultValue']
    elif var.data_type in list_data_types:
        var.default_value = ''
    else:
        var.default_value = '0'

    try:
        pdo_mapping = lines['PDOMapping']
        var.pdo_mapping = bool(int(pdo_mapping))
    except KeyError:
        pass  # optional
    except ValueError:
        errors.append(f'{_LEVEL}: PDOMapping value of {pdo_mapping} is invalid in {header}')

    if 'LowLimit' in lines:  # optional
        var.low_limit = lines['LowLimit']

    if 'HighLimit' in lines:  # optional
        var.high_limit = lines['HighLimit']

    if ';StorageLocation' in lines:  # optional, for CANopenNode support
        var.storage_location = lines[';StorageLocation']

    for i in lines:
        if i not in VARIABLE_ENTRIES:
            errors.append(f'{_LEVEL}: Unknown entry "{i}" in {header}')

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
        errors.append(f'{_LEVEL}: ParameterName was missing from {header}')
        arr.parameter_name = 'Unknown array name'

    if 'Denotation' in lines:
        arr.denotation = lines['Denotation']

    if ';StorageLocation' in lines:  # optional, for CANopenNode support
        arr.storage_location = lines[';StorageLocation']

    # NOTE: SubNumber is mandatory entry, but is not used by Array class

    for i in lines:
        if i not in ARRAY_RECORD_ENTRIES:
            errors.append(f'{_LEVEL}: Unknown entry "{i}" in {header}')

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
        errors.append(f'{_LEVEL}: ParameterName was missing from {header}')
        rec.parameter_name = 'Unknown record name'

    if 'Denotation' in lines:
        rec.denotation = lines['Denotation']

    if ';StorageLocation' in lines:  # optional, for CANopenNode support
        rec.storage_location = lines[';StorageLocation']

    # NOTE: SubNumber is mandatory entry, but is not used by Record class

    for i in lines:
        if i not in ARRAY_RECORD_ENTRIES:
            errors.append(f'{_LEVEL}: Unknown entry "{i}" in {header}')

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
        errors.append(f'{_LEVEL}: FileName was missing from {header}')

    try:
        file_info.file_version = _read_int_value(header, lines, 'FileVersion')
    except ValueError as exc:
        errors.append(f'{_LEVEL}: {exc}')

    try:
        file_info.file_revision = _read_int_value(header, lines, 'FileRevision')
    except ValueError as exc:
        errors.append(f'{_LEVEL}: {exc}')

    if file_info.file_name.endswith('.dcf'):  # only in DCFs
        try:
            file_info.last_eds = lines['LastEDS']
        except KeyError:
            errors.append(f'{_LEVEL}: LastEDS was missing from {header}')

    try:
        file_info.eds_version = lines['EDSVersion']
    except KeyError:
        # optional, if missing it's v3.0
        file_info.eds_version = '3.0'

    try:
        file_info.description = lines['Description']
    except KeyError:
        errors.append(f'{_LEVEL}: Description was missing from {header}')

    try:
        file_info.creation_dt = _read_datetime_value(header, lines, 'CreationTime',
                                                     'CreationDate')
    except ValueError as exc:
        errors.append(f'{_LEVEL}: {exc}')

    try:
        file_info.created_by = lines['CreatedBy']
    except KeyError:
        errors.append(f'{_LEVEL}: CreatedBy was missing from {header}')

    try:
        file_info.modification_dt = _read_datetime_value(header, lines, 'ModificationTime',
                                                         'ModificationDate')
    except ValueError as exc:
        errors.append(f'{_LEVEL}: {exc}')

    try:
        file_info.modified_by = lines['ModifiedBy']
    except KeyError:
        errors.append(f'{_LEVEL}: ModifiedBy was missing from {header}')

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
        device_info.vendor_name = lines['VendorName']
    except KeyError:
        errors.append(f'{_LEVEL}: VendorName was missing from {header}')

    try:
        device_info.vendor_number = _read_int_value(header, lines, 'VendorNumber')
    except ValueError as exc:
        errors.append(f'{_LEVEL}: {exc}')

    try:
        device_info.product_name = lines['ProductName']
    except KeyError:
        errors.append(f'{_LEVEL}: ProductName was missing from {header}')

    try:
        device_info.product_number = _read_int_value(header, lines, 'ProductNumber')
    except ValueError as exc:
        errors.append(f'{_LEVEL}: {exc}')

    try:
        device_info.revision_number = _read_int_value(header, lines, 'RevisionNumber')
    except ValueError as exc:
        errors.append(f'{_LEVEL}: {exc}')

    try:
        device_info.order_code = lines['OrderCode']
    except KeyError:
        errors.append(f'{_LEVEL}: OrderCode was missing from {header}')

    for i in BAUD_RATE:
        try:
            device_info.baud_rate[i] = _read_bool_value(header, lines, f'BaudRate_{i}')
        except ValueError as exc:
            errors.append(f'{_LEVEL}: {exc}')

    try:
        device_info.simple_boot_up_master = _read_bool_value(header, lines,
                                                             'SimpleBootUpMaster')
    except ValueError as exc:
        errors.append(f'{_LEVEL}: {exc}')

    try:
        device_info.simple_boot_up_slave = _read_bool_value(header, lines,
                                                            'SimpleBootUpSlave')
    except ValueError as exc:
        errors.append(f'{_LEVEL}: {exc}')

    try:
        device_info.grandularity = _read_int_value(header, lines, 'Granularity')
    except ValueError as exc:
        errors.append(f'{_LEVEL}: {exc}')

    try:
        device_info.dynamic_channel_supperted = _read_bool_value(header, lines,
                                                                 'DynamicChannelsSupported')
    except ValueError as exc:
        errors.append(f'{_LEVEL}: {exc}')

    try:
        device_info.num_of_rpdo = _read_int_value(header, lines, 'NrOfRXPDO')
    except ValueError as exc:
        errors.append(f'{_LEVEL}: {exc}')

    try:
        device_info.num_of_tpdo = _read_int_value(header, lines, 'NrOfTXPDO')
    except ValueError as exc:
        errors.append(f'{_LEVEL}: {exc}')

    try:
        device_info.lss_supported = _read_bool_value(header, lines, 'LSS_Supported')
    except ValueError as exc:
        errors.append(f'{_LEVEL}: {exc}')

    return device_info, errors


def _read_device_commissioning(header: str, lines: dict) -> (DeviceCommissioning, list):
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
        errors.append(f'{_LEVEL}: {exc}')

    try:
        device_comm.node_name = lines['NodeName']
    except KeyError:
        errors.append(f'{_LEVEL}: NodeName was missing from {header}')

    try:
        try:
            temp = _read_int_value(header, lines, 'Baudrate')
        except Exception:
            temp = _read_int_value(header, lines, 'BaudRate')
        if temp in BAUD_RATE:
            device_comm.baud_rate = temp
        else:
            errors.append(f'{_LEVEL}: Baudrate in {header} was not a valid CANopen baud rate')
    except ValueError as exc:
        errors.append(f'{_LEVEL}: {exc}')

    try:
        device_comm.net_number = _read_int_value(header, lines, 'NetNumber')
    except ValueError as exc:
        errors.append(f'{_LEVEL}: {exc}')

    try:
        device_comm.network_name = lines['NetworkName']
    except KeyError:
        errors.append(f'{_LEVEL}: NetworkName was missing from {header}')

    try:
        device_comm.canopen_manager = _read_bool_value(header, lines, 'CANopenManager')
    except ValueError as exc:
        errors.append(f'{_LEVEL}: {exc}')

    try:
        device_comm.lss_serialnumber = _read_bool_value(header, lines, 'LSS_SerialNumber')
    except ValueError as exc:
        errors.append(f'{_LEVEL}: {exc}')

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
        Values were missing or misformatted.

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
        Value were missing or misformatted.

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
        Values were missing or misformatted.

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
