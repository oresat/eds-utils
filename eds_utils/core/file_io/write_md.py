'''Everything to write an eds/dcf as a markdown file'''

from os.path import basename, splitext

from .. import BAUD_RATE, ObjectType
from ..objects import Variable, Array, Record
from ..eds import EDS


def write_md(eds: EDS, file_path='', dcf=False):
    '''Save an eds/dcf as a markdown file

    Parameters
    ----------
    eds: EDS
        eds data structure to save as file
    file_path: str
        File path of eds/dcf to save and must end with ".md". If empty the value from the eds data
        structure.
    dcf: bool
        Add dcf info to markdown file.
    '''

    lines = []

    if not file_path:  # use value from file info in eds
        file_path = splitext(eds.file_info.file_name)[0] + '.md'

    lines.append(f'# {eds.file_info.file_name}')
    lines.append('')

    # file info seciton
    lines.append('## File Info')
    lines.append('')
    lines.append('Item|Value')
    lines.append('---|---')
    lines.append(f'File Name|{basename(eds.file_info.file_name)}')
    lines.append(f'File Version|{eds.file_info.file_version}')
    lines.append(f'File Revision|{eds.file_info.file_revision}')
    if dcf:
        lines.append(f'Last EDS|{eds.file_info.last_eds}')
    lines.append(f'EDS Version|{eds.file_info.eds_version}')
    lines.append(f'Description|{eds.file_info.description}')
    lines.append('Creation Time|' + eds.file_info.creation_dt.strftime('%I:%M%p'))
    lines.append('Creation Date|' + eds.file_info.creation_dt.strftime('%m-%d-%Y'))
    lines.append(f'Created By|{eds.file_info.created_by}')
    lines.append('Modification Time|' + eds.file_info.modification_dt.strftime('%I:%M%p'))
    lines.append('Modification Date|' + eds.file_info.modification_dt.strftime('%m-%d-%Y'))
    lines.append(f'Modified By|{eds.file_info.modified_by}')
    lines.append('')

    # device info seciton
    lines.append('## Device Info')
    lines.append('')
    lines.append('Item|Value')
    lines.append('---|---')
    lines.append(f'Vendor Name|{eds.device_info.vendor_name}')
    lines.append(f'Vendor Number|{eds.device_info.vendor_number}')
    lines.append(f'Product Name|{eds.device_info.product_name}')
    lines.append(f'Product Number|{eds.device_info.product_number}')
    lines.append(f'Revision Number|{eds.device_info.revision_number}')
    lines.append(f'Order Code|{eds.device_info.order_code}')
    for i in BAUD_RATE:
        lines.append(f'BaudRate_{i}|{int(eds.device_info.baud_rate[i])}')
    lines.append(f'Simple Boot Up Master|{int(eds.device_info.simple_boot_up_master)}')
    lines.append(f'Simple Boot Up Slave|{int(eds.device_info.simple_boot_up_slave)}')
    lines.append(f'Granularity|{eds.device_info.grandularity}')
    lines.append(f'Dynamic Channels Supported|{int(eds.device_info.dynamic_channel_supperted)}')
    lines.append(f'Group Messaging|{int(eds.device_info.group_messaging)}')
    lines.append(f'Number of RPDOs|{eds.rpdos}')
    lines.append(f'Number of TPDOs|{eds.tpdos}')
    lines.append(f'LSS Supported|{int(eds.device_info.lss_supported)}')
    lines.append('')

    if dcf:
        lines.append('## Device Commissioning')
        lines.append('')
        lines.append('Item|Value')
        lines.append('---|---')
        lines.append(f'NodeID|0x{eds.device_commissioning.node_id:X}')
        lines.append(f'NodeName|{eds.device_commissioning.node_name}')
        lines.append(f'Baudrate|{eds.device_commissioning.baud_rate}')
        lines.append(f'NetNumber|{eds.device_commissioning.net_number}')
        lines.append(f'NetworkName|{eds.device_commissioning.network_name}')
        lines.append(f'CANopenManager|{int(eds.device_commissioning.canopen_manager)}')
        lines.append(f'LSS_SerialNumber|{eds.device_commissioning.lss_serialnumber}')
        lines.append('')
        lines.append('')

    # TODO dummy usage
    lines.append('## Dummy Usage')
    lines.append('')
    lines.append('Item|Value')
    lines.append('---|---')
    for i in range(8):
        lines.append(f'Dummy000{i}|1')
    lines.append('')

    # TODO comments
    lines.append('## Comments')
    lines.append('')
    lines.append('TBD')
    lines.append('')

    lines.append('## Objects')
    lines.append('')
    lines += _objects_lines(eds, eds.indexes)

    # remove trailing new line
    lines = lines[:-1]

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

    if subindex is None:
        lines.append(f'### {variable.parameter_name} (index 0x{index:X})')
    else:
        lines.append(f'#### {variable.parameter_name} (index 0x{index:X} - '
                     f'subindex 0x{subindex:X})')
    lines.append('')

    if variable.comments:
        for i in variable.comments.split('\n'):
            lines.append(f'{i}')
        lines.append('')

    lines.append('Item|Value')
    lines.append('---|---')
    if dcf and variable.denotation:
        lines.append(f'Denotation|{variable.denotation}')
    lines.append(f'Object Type|{ObjectType.VAR.name}')
    if canopennode:  # optional, for CANopenNode suppport
        lines.append(f'Storage Location|{variable.storage_location}')
    lines.append(f'Data Type|{variable.data_type.name}')
    lines.append(f'Access Type|{variable.access_type.to_str()}')
    if variable.default_value:  # optional
        lines.append(f'Default Value|{variable.default_value}')
    if variable.pdo_mapping:  # optional
        lines.append(f'PDO Mapping|{int(variable.pdo_mapping)}')
    if variable.low_limit:  # optional
        lines.append(f'Low Limit|{variable.low_limit}')
    if variable.high_limit:  # optional
        lines.append(f'High Limit|{variable.high_limit}')
    lines.append('')

    return lines


def _array_lines(array: Array, index: int, dcf=False, canopennode=False) -> list:
    lines = []

    lines.append(f'### {array.parameter_name} (index 0x{index:X})')
    lines.append('')

    if array.comments:
        for i in array.comments.split('\n'):
            lines.append(f'{i}')
        lines.append('')

    lines.append('Item|Value')
    lines.append('---|---')
    if dcf and array.denotation:
        lines.append(f'Denotation|{array.denotation}')
    lines.append(f'Object Type|{ObjectType.ARRAY.name}')
    lines.append(f'Subindexes|{len(array)}')
    lines.append('')

    for i in array.subindexes:
        lines += _variable_lines(array[i], index, i, dcf, canopennode)

    return lines


def _record_lines(record: Record, index: int, dcf=False, canopennode=False) -> list:
    lines = []

    lines.append(f'### {record.parameter_name} (index 0x{index:X})')
    lines.append('')

    if record.comments:
        for i in record.comments.split('\n'):
            lines.append(f'{i}')
        lines.append('')

    lines.append('Item|Value')
    lines.append('---|---')
    if dcf and record.denotation:
        lines.append(f'Denotation|{record.denotation}')
    lines.append(f'Object Type|{ObjectType.RECORD.name}')
    lines.append(f'Subindexes|{len(record)}')
    lines.append('')

    for i in record.subindexes:
        lines += _variable_lines(record[i], index, i, dcf, canopennode)

    return lines
