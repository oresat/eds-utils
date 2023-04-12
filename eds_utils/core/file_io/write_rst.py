'''Everything to write an eds/dcf as a reStructuredText file'''

from os.path import basename, splitext

from . import INDENT3
from .. import BAUD_RATE, ObjectType
from ..objects import Variable, Array, Record
from ..eds import EDS


def write_rst(eds: EDS, file_path='', dcf=False):
    '''Save an eds/dcf as a reStructuredText file

    Parameters
    ----------
    eds: EDS
        eds data structure to save as file
    file_path: str
        File path of eds/dcf to save and must end with ".rst". If empty the value from the eds data
        structure.
    dcf: bool
        Add dcf info to markdown file.
    '''

    lines = []

    if not file_path:  # use value from file info in eds
        file_path = splitext(eds.file_info.file_name)[0] + '.rst'

    title = eds.file_info.file_name
    lines.append('#' * len(title))
    lines.append(title)
    lines.append('#' * len(title))
    lines.append('')

    # file info section
    lines.append('File Info')
    lines.append('#########')
    lines.append('')
    lines.append('.. csv-table::')
    lines.append('')
    lines.append(f'{INDENT3}"File Name", "{basename(eds.file_info.file_name)}"')
    lines.append(f'{INDENT3}"File Version", "{eds.file_info.file_version}"')
    lines.append(f'{INDENT3}"File Revision", "{eds.file_info.file_revision}"')
    if dcf:
        lines.append(f'{INDENT3}"Last EDS", "{eds.file_info.last_eds}"')
    lines.append(f'{INDENT3}"EDS Version", "{eds.file_info.eds_version}"')
    lines.append(f'{INDENT3}"Description", "{eds.file_info.description}"')
    time_str = eds.file_info.creation_dt.strftime('%I:%M%p')
    lines.append(f'{INDENT3}"Creation Time", "{time_str}"')
    date_str = eds.file_info.creation_dt.strftime('%m-%d-%Y')
    lines.append(f'{INDENT3}"Creation Date", "{date_str}"')
    lines.append(f'{INDENT3}"Created By", "{eds.file_info.created_by}"')
    time_str = eds.file_info.modification_dt.strftime('%I:%M%p')
    lines.append(f'{INDENT3}"Modification Time", "{time_str}"')
    date_str = eds.file_info.modification_dt.strftime('%m-%d-%Y')
    lines.append(f'{INDENT3}"Modification Date", "{date_str}"')
    lines.append(f'{INDENT3}"Modified By", "{eds.file_info.modified_by}"')
    lines.append('')

    # device info section
    lines.append('Device Info')
    lines.append('###########')
    lines.append('')
    lines.append('.. csv-table::')
    lines.append('')
    lines.append(f'{INDENT3}"Vendor Name", "{eds.device_info.vendor_name}"')
    lines.append(f'{INDENT3}"Vendor Number", "{eds.device_info.vendor_number}"')
    lines.append(f'{INDENT3}"Product Name", "{eds.device_info.product_name}"')
    lines.append(f'{INDENT3}"Product Number", "{eds.device_info.product_number}"')
    lines.append(f'{INDENT3}"Revision Number", "{eds.device_info.revision_number}"')
    lines.append(f'{INDENT3}"Order Code", "{eds.device_info.order_code}"')
    for i in BAUD_RATE:
        lines.append(f'{INDENT3}"Baud Rate {i}", "{int(eds.device_info.baud_rate[i])}"')
    temp = int(eds.device_info.simple_boot_up_master)
    lines.append(f'{INDENT3}"Simple Boot Up Master", "{temp}"')
    lines.append(f'{INDENT3}"Simple Boot Up Slave", "{int(eds.device_info.simple_boot_up_slave)}"')
    lines.append(f'{INDENT3}"Granularity", "{eds.device_info.grandularity}"')
    temp = int(eds.device_info.dynamic_channel_supperted)
    line = f'{INDENT3}"Dynamic Channels Supported", "{temp}"'
    lines.append(line)
    lines.append(f'{INDENT3}"Group Messaging", "{int(eds.device_info.group_messaging)}"')
    lines.append(f'{INDENT3}"Number of RPDOs", "{eds.rpdos}"')
    lines.append(f'{INDENT3}"Number of TPDOs", "{eds.tpdos}"')
    lines.append(f'{INDENT3}"LSS Supported", "{int(eds.device_info.lss_supported)}"')
    lines.append('')

    if dcf:
        lines.append('Device Commissioning')
        lines.append('####################')
        lines.append('')
        lines.append('.. csv-table::')
        lines.append('')
        lines.append(f'{INDENT3}"Node ID", "0x{eds.device_commissioning.node_id:X}"')
        lines.append(f'{INDENT3}"Node Name", "{eds.device_commissioning.node_name}"')
        lines.append(f'{INDENT3}"Baudrate", "{eds.device_commissioning.baud_rate}"')
        lines.append(f'{INDENT3}"Net Number", "{eds.device_commissioning.net_number}"')
        lines.append(f'{INDENT3}"Network Name", "{eds.device_commissioning.network_name}"')
        temp = int(eds.device_commissioning.canopen_manager)
        lines.append(f'{INDENT3}"CANopen Manager", "{temp}"')
        temp = eds.device_commissioning.lss_serialnumber
        lines.append(f'{INDENT3}"LSS Serial Number", "{temp}"')
        lines.append('')

    # TODO dummy usage
    lines.append('Dummy Usage')
    lines.append('###########')
    lines.append('')
    lines.append('.. csv-table::')
    lines.append('')
    for i in range(8):
        lines.append(f'{INDENT3}"Dummy000{i}", "1"')
    lines.append('')

    # TODO comments
    lines.append('Comments')
    lines.append('###########')
    lines.append('')
    lines.append('TBD')
    lines.append('')

    lines.append('Objects')
    lines.append('#######')
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
        title = f'{variable.parameter_name} (index 0x{index:X})'
        lines.append(title)
        lines.append('-' * len(title))
    else:
        title = f'{variable.parameter_name} (index 0x{index:X} - subindex 0x{subindex:X})'
        lines.append(title)
        lines.append('*' * len(title))
    lines.append('')

    if variable.comments:
        for i in variable.comments.split('\n'):
            lines.append(f'{i}')
        lines.append('')

    lines.append('.. csv-table::')
    lines.append('')
    if dcf and variable.denotation:
        lines.append(f'{INDENT3}"Denotation", "{variable.denotation}"')
    lines.append(f'{INDENT3}"Object Type", "{ObjectType.VAR.name}"')
    if canopennode:  # optional, for CANopenNode suppport
        lines.append(f'{INDENT3}"Storage Location", "{variable.storage_location}"')
    lines.append(f'{INDENT3}"Data Type", "{variable.data_type.name}"')
    lines.append(f'{INDENT3}"Access Type", "{variable.access_type.to_str()}"')
    if variable.default_value:  # optional
        lines.append(f'{INDENT3}"Default Value", "{variable.default_value}"')
    if variable.pdo_mapping:  # optional
        lines.append(f'{INDENT3}"PDO Mapping", "{int(variable.pdo_mapping)}"')
    if variable.low_limit:  # optional
        lines.append(f'{INDENT3}"Low Limit", "{variable.low_limit}"')
    if variable.high_limit:  # optional
        lines.append(f'{INDENT3}"High Limit", "{variable.high_limit}"')
    lines.append('')

    return lines


def _array_lines(array: Array, index: int, dcf=False, canopennode=False) -> list:
    lines = []

    title = f'{array.parameter_name} (index 0x{index:X})'
    lines.append(title)
    lines.append('-' * len(title))
    lines.append('')

    if array.comments:
        for i in array.comments.split('\n'):
            lines.append(f'{i}')
        lines.append('')

    lines.append('.. csv-table::')
    lines.append('')
    if dcf and array.denotation:
        lines.append(f'{INDENT3}"Denotation", "{array.denotation}"')
    lines.append(f'{INDENT3}"Object Type", "{ObjectType.ARRAY.name}"')
    lines.append(f'{INDENT3}"Subindexes", "{len(array)}"')
    lines.append('')

    for i in array.subindexes:
        lines += _variable_lines(array[i], index, i, dcf, canopennode)

    return lines


def _record_lines(record: Record, index: int, dcf=False, canopennode=False) -> list:
    lines = []

    title = f'{record.parameter_name} (index 0x{index:X})'
    lines.append(title)
    lines.append('-' * len(title))
    lines.append('')

    if record.comments:
        for i in record.comments.split('\n'):
            lines.append(f'{i}')
        lines.append('')

    lines.append('.. csv-table::')
    lines.append('')
    if dcf and record.denotation:
        lines.append(f'{INDENT3}"Denotation", "{record.denotation}"')
    lines.append(f'{INDENT3}"Object Type", "{ObjectType.RECORD.name}"')
    lines.append(f'{INDENT3}"Subindexes", "{len(record)}"')
    lines.append('')

    for i in record.subindexes:
        lines += _variable_lines(record[i], index, i, dcf, canopennode)

    return lines
