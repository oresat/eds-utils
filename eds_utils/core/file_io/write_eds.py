'''Everything to write an eds/dcf file'''

from os.path import basename, splitext

from .. import BAUD_RATE, ObjectType, AccessType, DataType
from ..objects import Variable, Array, Record
from ..eds import EDS


def write_eds(eds: EDS, file_path='', dcf=False):
    '''Save an eds/dcf file

    Parameters
    ----------
    eds: EDS
        eds data structure to save as file
    file_path: str
        File path of eds/dcf to save. If empty the value from the eds data structure.
    dcf: bool
        Force the file save to be to a dcf file reguardless if the file_path ends with ".dcf"
    '''

    lines = []

    if not file_path:  # use value from file info
        file_path = eds.file_info.file_name

    if not dcf and file_path.endswith('.dcf'):
        dcf = True
    elif dcf and file_path.endswith('.eds'):  # force eds to dcf
        eds.file_info.last_eds = basename(file_path)
        file_path = splitext(file_path)[0] + '.dcf'

    # file info seciton
    lines.append('[FileInfo]')
    lines.append(f'FileName={basename(file_path)}')
    lines.append(f'FileVersion={eds.file_info.file_version}')
    lines.append(f'FileRevision={eds.file_info.file_revision}')
    if dcf:
        lines.append(f'LastEDS={eds.file_info.last_eds}')
    lines.append(f'EDSVersion={eds.file_info.eds_version}')
    lines.append(f'Description={eds.file_info.description}')
    lines.append('CreationTime=' + eds.file_info.creation_dt.strftime('%I:%M%p'))
    lines.append('CreationDate=' + eds.file_info.creation_dt.strftime('%m-%d-%Y'))
    lines.append(f'CreatedBy={eds.file_info.created_by}')
    lines.append('ModificationTime=' + eds.file_info.modification_dt.strftime('%I:%M%p'))
    lines.append('ModificationDate=' + eds.file_info.modification_dt.strftime('%m-%d-%Y'))
    lines.append(f'ModifiedBy={eds.file_info.modified_by}')
    lines.append('')

    # device info seciton
    lines.append('[DeviceInfo]')
    lines.append(f'VendorName={eds.device_info.vendor_name}')
    lines.append(f'VendorNumber={eds.device_info.vendor_number}')
    lines.append(f'ProductName={eds.device_info.product_name}')
    lines.append(f'ProductNumber={eds.device_info.product_number}')
    lines.append(f'RevisionNumber={eds.device_info.revision_number}')
    lines.append(f'OrderCode={eds.device_info.order_code}')
    for i in BAUD_RATE:
        lines.append(f'BaudRate_{i}={int(eds.device_info.baud_rate[i])}')
    lines.append(f'SimpleBootUpMaster={int(eds.device_info.simple_boot_up_master)}')
    lines.append(f'SimpleBootUpSlave={int(eds.device_info.simple_boot_up_slave)}')
    lines.append(f'Granularity={eds.device_info.grandularity}')
    lines.append(f'DynamicChannelsSupported={int(eds.device_info.dynamic_channel_supperted)}')
    lines.append(f'GroupMessaging={int(eds.device_info.group_messaging)}')
    lines.append(f'NrOfRXPDO={eds.rpdos}')
    lines.append(f'NrOfTXPDO={eds.tpdos}')
    lines.append(f'LSS_Supported={int(eds.device_info.lss_supported)}')
    lines.append('')

    if dcf:
        lines.append('[DeviceComissioning]')  # only one 'm' in header
        lines.append(f'NodeID=0x{eds.device_commissioning.node_id:X}')
        lines.append(f'NodeName={eds.device_commissioning.node_name}')
        lines.append(f'BaudRate={eds.device_commissioning.baud_rate}')
        lines.append(f'NetNumber={eds.device_commissioning.net_number}')
        lines.append(f'NetworkName={eds.device_commissioning.network_name}')
        lines.append(f'CANopenManager={int(eds.device_commissioning.canopen_manager)}')
        lines.append(f'LSS_SerialNumber={int(eds.device_commissioning.lss_serialnumber)}')
        lines.append('')

    # TODO dummy usage
    lines.append('[DummyUsage]')
    for i in range(8):
        lines.append(f'Dummy000{i}=1')
    lines.append('')

    # TODO comments
    lines.append('[Comments]')
    lines.append('Lines=0')
    lines.append('')

    lines.append('[MandatoryObjects]')
    mandatory_objs = eds.mandatory_objects
    lines.append(f'SupportedObjects={len(mandatory_objs)}')
    for i in mandatory_objs:
        num = mandatory_objs.index(i) + 1
        value = f'0x{i:04X}'
        lines.append(f'{num}={value}')
    lines.append('')

    lines += _objects_lines(eds, mandatory_objs)

    lines.append('[OptionalObjects]')
    optional_objs = eds.optional_objects
    lines.append(f'SupportedObjects={len(optional_objs)}')
    for i in optional_objs:
        num = optional_objs.index(i) + 1
        value = f'0x{i:04X}'
        lines.append(f'{num}={value}')
    lines.append('')

    lines += _objects_lines(eds, optional_objs)

    lines.append('[ManufacturerObjects]')
    manufacturer_objs = eds.manufacturer_objects
    lines.append(f'SupportedObjects={len(manufacturer_objs)}')
    for i in manufacturer_objs:
        num = manufacturer_objs.index(i) + 1
        value = f'0x{i:04X}'
        lines.append(f'{num}={value}')
    lines.append('')

    lines += _objects_lines(eds, manufacturer_objs)

    with open(file_path, 'w') as f:
        for i in lines:
            f.write(i + '\n')


def _objects_lines(eds: EDS, indexes: list, dcf=False) -> list:
    lines = []

    for i in indexes:
        obj = eds[i]
        if isinstance(obj, Variable):
            lines += _variable_lines(obj, i, dcf=dcf, canopennode=eds.canopennode)
        elif isinstance(obj, Array):
            lines += _array_lines(obj, i, dcf=dcf, canopennode=eds.canopennode)
        elif isinstance(obj, Record):
            lines += _record_lines(obj, i, dcf=dcf, canopennode=eds.canopennode)

    return lines


def _variable_lines(variable: Variable, index: int, subindex=None, dcf=False,
                    canopennode=False) -> list:
    lines = []

    if variable.comments:
        for i in variable.comments.split('\n'):
            lines.append(f';{i}')

    if subindex is None:
        lines.append(f'[{index:X}]')
    else:
        lines.append(f'[{index:X}sub{subindex:X}]')

    lines.append(f'ParameterName={variable.parameter_name}')
    if dcf and variable.denotation:
        lines.append(f'Denotation={variable.denotation}')
    lines.append(f'ObjectType={ObjectType.VAR.to_str()}')
    if canopennode:  # optional, for CANopenNode suppport
        lines.append(f';StorageLocation={variable.storage_location}')
    lines.append(f'DataType={variable.data_type.to_str()}')
    if subindex == 0:
        lines.append(f'AccessType={AccessType.CONST.to_str()}')
    else:
        lines.append(f'AccessType={variable.access_type.to_str()}')
    if variable.default_value:  # optional
        if variable.data_type == DataType.OCTET_STRING:
            value_ns = variable.default_value.replace(' ', '')
            tmp = ' '.join([value_ns[i: i + 2] for i in range(0, len(value_ns), 2)])
            lines.append(f'DefaultValue={tmp}')
        else:
            lines.append(f'DefaultValue={variable.default_value}')
    if variable.pdo_mapping:  # optional
        lines.append(f'PDOMapping={int(variable.pdo_mapping)}')
    if variable.low_limit:  # optional
        lines.append(f'LowLimit={variable.low_limit}')
    if variable.high_limit:  # optional
        lines.append(f'HighLimit={variable.high_limit}')
    lines.append('')

    return lines


def _array_lines(array: Array, index: int, dcf=False, canopennode=False) -> list:
    lines = []

    if array.comments:
        for i in array.comments.split('\n'):
            lines.append(f';{i}')

    lines.append(f'[{index:X}]')

    lines.append(f'ParameterName={array.parameter_name}')
    if dcf and array.denotation:
        lines.append(f'Denotation={array.denotation}')
    lines.append(f'ObjectType={ObjectType.ARRAY.to_str()}')
    if canopennode:  # optional, for CANopenNode suppport
        lines.append(f';StorageLocation={array.storage_location}')
    lines.append(f'SubNumber={len(array)}')
    lines.append('')

    for i in array.subindexes:
        lines += _variable_lines(array[i], index, i, dcf, canopennode)

    return lines


def _record_lines(record: Record, index: int, dcf=False, canopennode=False) -> list:
    lines = []

    if record.comments:
        for i in record.comments.split('\n'):
            lines.append(f';{i}')

    lines.append(f'[{index:X}]')

    lines.append(f'ParameterName={record.parameter_name}')
    if dcf and record.denotation:
        lines.append(f'Denotation={record.denotation}')
    lines.append(f'ObjectType={ObjectType.RECORD.to_str()}')
    if canopennode:  # optional, for CANopenNode suppport
        lines.append(f';StorageLocation={record.storage_location}')
    lines.append(f'SubNumber={len(record)}')
    lines.append('')

    for i in record.subindexes:
        lines += _variable_lines(record[i], index, i, dcf, canopennode)

    return lines
