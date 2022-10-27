'''Everything to write an eds/dcf as CANopenNode OD.[c/h] files'''

from . import INDENT4, INDENT8, INDENT16
from .. import ObjectType, DataType, StorageLocation, AccessType
from ..eds import EDS
from ..objects import Variable

DATA_TYPE_LENGTH = {
    DataType.BOOLEAN: 1,
    DataType.INTEGER8: 1,
    DataType.INTEGER16: 2,
    DataType.INTEGER32: 4,
    DataType.UNSIGNED8: 1,
    DataType.UNSIGNED16: 2,
    DataType.UNSIGNED32: 4,
    DataType.REAL32: 4,
    DataType.VISIBLE_STRING: 0,
    DataType.OCTET_STRING: 0,
    DataType.UNICODE_STRING: 0,
    DataType.TIME_OF_DAY: 6,
    DataType.TIME_DIFFERENCE: 6,
    DataType.DOMAIN: 0,
    DataType.INTEGER24: 3,
    DataType.REAL64: 8,
    DataType.INTEGER40: 5,
    DataType.INTEGER48: 6,
    DataType.INTEGER56: 7,
    DataType.INTEGER64: 8,
    DataType.UNSIGNED24: 3,
    DataType.UNSIGNED40: 5,
    DataType.UNSIGNED48: 6,
    DataType.UNSIGNED56: 7,
    DataType.UNSIGNED64: 8,
}

DATA_TYPE_STR = [
    DataType.VISIBLE_STRING,
    DataType.OCTET_STRING,
    DataType.UNICODE_STRING,
]

DATA_TYPE_C_TYPES = {
    DataType.BOOLEAN: 'bool',
    DataType.INTEGER8: 'int8_t',
    DataType.INTEGER16: 'int16_t',
    DataType.INTEGER32: 'int32_t',
    DataType.UNSIGNED8: 'uint8_t',
    DataType.UNSIGNED16: 'uint16_t',
    DataType.UNSIGNED32: 'uint32_t',
    DataType.REAL32: 'float',
    DataType.VISIBLE_STRING: 'char',
    DataType.OCTET_STRING: 'uint8_t',
    DataType.UNICODE_STRING: 'char',
    DataType.DOMAIN: '0',
    DataType.REAL64: 'double',
    DataType.INTEGER64: 'int64_t',
    DataType.UNSIGNED64: 'uint64_t',
}


def camel_case(string: str) -> str:
    '''Convert string to camelCase'''

    if len(string) == 0:
        return ''  # nothing to do

    # remove invalid chars for variable names in C
    s = string.replace('-', ' ').replace('_', ' ').replace('(', ' ').replace(')', ' ')
    s = s.replace('  ', ' ')

    s = s.split()

    name = ''
    for i in s:

        number = True
        try:
            int(i)
        except ValueError:
            number = False

        if number:
            name += f'_{i}_'  # add '_' arounds numbers
        elif len(i) > 1 and i == i.upper():  # acronym
            name += i + '_'  # add '_' after acronym
        else:
            name += i.capitalize()

    # if the 1st word is not a acronym, make sure the 1st char is a lowercase
    if name[:2] != name[:2].upper():
        name = name[0].lower() + name[1:]

    # remove any trailing '_'
    if name[-1] == '_':
        name = name[:-1]

    name = name.replace('__', '_')

    return name


def write_canopennode(eds: EDS, dir_path=''):
    '''Save an eds/dcf as CANopenNode OD.[c/h] files

    Parameters
    ----------
    eds: EDS
        eds data structure to save as file
    dir_path: str
        Path to directory to output OD.[c/h] to. If not set the same dir path as the eds will
        be used.
    '''

    write_canopennode_c(eds, dir_path)
    write_canopennode_h(eds, dir_path)


def remove_node_id(default_value: str) -> str:
    '''Remove "+$NODEID" or '$NODEID+" from the default value'''

    temp = default_value.split('+')

    if len(temp) == 1:
        return default_value  # does not include $NODEID
    elif temp[0] == '$NODEID':
        return temp[1].rsplit()
    elif temp[1] == '$NODEID':
        return temp[0].rsplit()

    return default_value  # does not include $NODEID


def attr_lines(eds: EDS, index: int) -> list:
    '''Generate attr lines for OD.c for a sepecific index'''

    lines = []

    obj = eds[index]
    if obj.object_type == ObjectType.VAR:
        default_value = remove_node_id(obj.default_value)
        line = f'{INDENT4}.x{index:X}_{camel_case(obj.parameter_name)} = '
        if obj.data_type == DataType.VISIBLE_STRING:
            line += f'"{default_value}",'
        elif obj.data_type == DataType.OCTET_STRING:
            line += '{'
            for i in range(0, len(obj.default_value), 2):
                line += f'0x{obj.default_value[i]}{obj.default_value[i+1]}, '
            line = line[:-2]
            line += '},'
        else:
            line += f'{default_value},'
        lines.append(line)
    elif obj.object_type == ObjectType.ARRAY:
        name = camel_case(obj.parameter_name)
        lines.append(f'{INDENT4}.x{index:X}_{name}_sub0 = {obj[0].default_value},')
        line = f'{INDENT4}.x{index:X}_{name} = ' + '{'
        for i in obj.subindexes[1:]:
            default_value = remove_node_id(obj[i].default_value)
            line += f'{default_value}, '
        line = line[:-2]  # remove trailing ','
        line += '},'
        lines.append(line)
    else:
        lines.append(f'{INDENT4}.x{index:X}_{camel_case(obj.parameter_name)} = ' + '{')
        for i in obj.subindexes:
            name = camel_case(obj[i].parameter_name)
            default_value = remove_node_id(obj[i].default_value)
            lines.append(f'{INDENT8}.{name} = {default_value},')
        lines.append(INDENT4 + '},')

    return lines


def _var_data_type_len(var: Variable) -> int:
    '''Get the length of the variable's data'''

    if var.data_type in DATA_TYPE_STR:
        length = len(var.default_value)
    else:
        length = DATA_TYPE_LENGTH[var.data_type]

    return length


def _var_attr_flags(var: Variable) -> str:
    '''Generate the variable attribute flags str'''

    attr_str = ''

    if var.access_type in [AccessType.RO, AccessType.CONST]:
        attr_str += 'ODA_SDO_R'
        if var.pdo_mapping:
            attr_str += ' | ODA_TPDO'
    elif var.access_type == AccessType.WO:
        attr_str += 'ODA_SDO_W'
        if var.pdo_mapping:
            attr_str += ' | ODA_RPDO'
    else:
        attr_str += 'ODA_SDO_RW'
        if var.pdo_mapping:
            attr_str += ' | ODA_TRPDO'

    if var.data_type in [DataType.VISIBLE_STRING, DataType.UNICODE_STRING]:
        attr_str += ' | ODA_STR'
    elif DATA_TYPE_LENGTH[var.data_type] > 1:
        attr_str += ' | ODA_MB'

    return attr_str


def obj_lines(eds: EDS, index) -> list:
    '''Generate object lines for OD.c for a sepecific index'''

    lines = []

    obj = eds[index]
    name = camel_case(obj.parameter_name)
    lines.append(f'{INDENT4}.o_{index:X}_{name} = ' + '{')
    if obj.object_type == ObjectType.VAR:
        st_loc = obj.storage_location.name
        if obj.data_type == DataType.VISIBLE_STRING:
            lines.append(f'{INDENT8}.dataOrig = &OD_{st_loc}.x{index:X}_{name}[0],')
            lines.append(f'{INDENT8}.attribute = {_var_attr_flags(obj)},')
            lines.append(f'{INDENT8}.dataLength = {_var_data_type_len(obj)}')
        elif obj.data_type == DataType.OCTET_STRING:
            lines.append(f'{INDENT8}.dataOrig = &OD_{st_loc}.x{index:X}_{name}[0],')
            lines.append(f'{INDENT8}.attribute = {_var_attr_flags(obj)},')
            lines.append(f'{INDENT8}.dataLength = {_var_data_type_len(obj) // 2}')
        else:
            lines.append(f'{INDENT8}.dataOrig = &OD_{st_loc}.x{index:X}_{name},')
            lines.append(f'{INDENT8}.attribute = {_var_attr_flags(obj)},')
            lines.append(f'{INDENT8}.dataLength = {_var_data_type_len(obj)}')
    elif obj.object_type == ObjectType.ARRAY:
        st_loc = obj.storage_location.name
        lines.append(f'{INDENT8}.dataOrig0 = &OD_{st_loc}.x{index:X}_{name}_sub0,')
        lines.append(f'{INDENT8}.dataOrig = &OD_{st_loc}.x{index:X}_{name}[0],')
        lines.append(f'{INDENT8}.attribute0 = ODA_SDO_R,')
        lines.append(f'{INDENT8}.attribute = {_var_attr_flags(obj[1])},')
        length = _var_data_type_len(obj)
        lines.append(f'{INDENT8}.dataElementLength = {length},')
        if length > 0 and length <= 8:
            lines.append(f'{INDENT8}.dataElementSizeof = sizeof(uint{8 * length}_t)')
    else:
        for i in obj.subindexes:
            st_loc = obj.storage_location.name
            name_sub = camel_case(obj[i].parameter_name)
            lines.append(INDENT8 + '{')
            lines.append(f'{INDENT16}.dataOrig = &OD_{st_loc}.x{index:X}_{name}.{name_sub},')
            lines.append(f'{INDENT16}.subIndex = {i},')
            lines.append(f'{INDENT16}.attribute = {_var_attr_flags(obj[i])},')
            lines.append(f'{INDENT16}.dataLength = {_var_data_type_len(obj[i])}')
            lines.append(INDENT8 + '},')
    lines.append(INDENT4 + '},')

    return lines


def write_canopennode_c(eds: EDS, dir_path=''):
    '''Save an eds/dcf as a CANopenNode OD.c file

    Parameters
    ----------
    eds: EDS
        eds data structure to save as file
    dir_path: str
        Path to directory to output OD.c to. If not set the same dir path as the eds will
        be used.
    '''

    lines = []

    if dir_path:
        file_path = dir_path + '/OD.c'
    else:  # use value eds/dcf path
        file_path = 'OD.c'

    lines.append('#define OD_DEFINITION')
    lines.append('#include "301/CO_ODinterface.h"')
    lines.append('#include "OD.h"')
    lines.append('')

    lines.append('#if CO_VERSION_MAJOR < 4')
    lines.append('#error This object dictionary is only comatible with CANopenNode v4 and above')
    lines.append('#endif')
    lines.append('')

    lines.append('OD_ATTR_ROM OD_ROM_t OD_ROM = {')
    for i in eds.indexes:
        if eds[i].storage_location == StorageLocation.ROM:
            lines += attr_lines(eds, i)
    lines.append('};')
    lines.append('')

    lines.append('OD_ATTR_RAM OD_RAM_t OD_RAM = {')
    for i in eds.indexes:
        if eds[i].storage_location == StorageLocation.RAM:
            lines += attr_lines(eds, i)
    lines.append('};')
    lines.append('')

    lines.append('OD_ATTR_PERSIST_COMM OD_PERSIST_COMM_t OD_PERSIST_COMM = {')
    for i in eds.indexes:
        if eds[i].storage_location == StorageLocation.PERSIST_COMM:
            lines += attr_lines(eds, i)
    lines.append('};')
    lines.append('')

    lines.append('OD_ATTR_PERSIST_MFR OD_PERSIST_MFR_t OD_PERSIST_MFR = {')
    for i in eds.indexes:
        if eds[i].storage_location == StorageLocation.PERSIST_MFR:
            lines += attr_lines(eds, i)
    lines.append('};')
    lines.append('')

    lines.append('typedef struct {')
    for i in eds.indexes:
        name = camel_case(eds[i].parameter_name)
        if eds[i].object_type == ObjectType.VAR:
            lines.append(f'{INDENT4}OD_obj_var_t o_{i:X}_{name};')
        elif eds[i].object_type == ObjectType.ARRAY:
            lines.append(f'{INDENT4}OD_obj_array_t o_{i:X}_{name};')
        else:
            size = len(eds[i])
            lines.append(f'{INDENT4}OD_obj_record_t o_{i:X}_{name}[{size}];')
    lines.append('} ODObjs_t;')
    lines.append('')

    lines.append('static CO_PROGMEM ODObjs_t ODObjs = {')
    for i in eds.indexes:
        lines += obj_lines(eds, i)
    lines.append('};')
    lines.append('')

    lines.append('static OD_ATTR_OD OD_entry_t ODList[] = {')
    for i in eds.indexes:
        name = camel_case(eds[i].parameter_name)
        if eds[i].object_type == ObjectType.VAR:
            length = 1
            obj_type = 'ODT_VAR'
        elif eds[i].object_type == ObjectType.ARRAY:
            length = len(eds[i])
            obj_type = 'ODT_ARR'
        else:
            length = len(eds[i])
            obj_type = 'ODT_REC'
        temp = f'0x{i:X}, 0x{length:02X}, {obj_type}, &ODObjs.o_{i:X}_{name}, NULL'
        lines.append(INDENT4 + '{' + temp + '},')
    lines.append(INDENT4 + '{0x0000, 0x00, 0, NULL, NULL}')
    lines.append('};')
    lines.append('')

    lines.append('static OD_t _OD = {')
    lines.append(f'{INDENT4}(sizeof(ODList) / sizeof(ODList[0])) - 1,')
    lines.append(f'{INDENT4}&ODList[0]')
    lines.append('};')
    lines.append('')

    lines.append('OD_t *OD = &_OD;')

    with open(file_path, 'w') as f:
        for i in lines:
            f.write(i + '\n')


def _canopennode_h_lines(eds: EDS, index: int) -> list:
    '''Generate struct lines for OD.h for a sepecific index'''

    lines = []

    obj = eds[index]
    name = camel_case(obj.parameter_name)

    if obj.object_type == ObjectType.VAR:
        c_name = DATA_TYPE_C_TYPES[obj.data_type]
        if obj.data_type == DataType.VISIBLE_STRING:
            length = len(obj.default_value) + 1  # add 1 for '\0'
            lines.append(f'{INDENT4}{c_name} x{index:X}_{name}[{length}];')
        elif obj.data_type == DataType.OCTET_STRING:
            length = len(obj.default_value) // 2  # aka number of uint8s
            lines.append(f'{INDENT4}{c_name} x{index:X}_{name}[{length}];')
        else:
            lines.append(f'{INDENT4}{c_name} x{index:X}_{name};')
    elif obj.object_type == ObjectType.ARRAY:
        c_name = DATA_TYPE_C_TYPES[obj.data_type]
        length = f'OD_CNT_ARR_{index:X}'
        lines.append(f'{INDENT4}uint8_t x{index:X}_{name}_sub0;')
        lines.append(f'{INDENT4}{c_name} x{index:X}_{name}[{length}];')
    else:
        lines.append(INDENT4 + 'struct {')
        for i in obj.subindexes:
            c_name = DATA_TYPE_C_TYPES[obj[i].data_type]
            sub_name = camel_case(obj[i].parameter_name)
            lines.append(f'{INDENT8}{c_name} {sub_name};')
        lines.append(INDENT4 + '}' + f' x{index:X}_{name};')

    return lines


def write_canopennode_h(eds: EDS, dir_path=''):
    '''Save an eds/dcf as a CANopenNode OD.h file

    Parameters
    ----------
    eds: EDS
        eds data structure to save as file
    dir_path: str
        Path to directory to output OD.h to. If not set the same dir path as the eds will
        be used.
    '''

    lines = []

    if dir_path:
        file_path = dir_path + '/OD.h'
    else:  # use value eds/dcf path
        file_path = 'OD.h'

    lines.append('#ifndef OD_H')
    lines.append('#define OD_H')
    lines.append('')

    lines.append('#define OD_CNT_NMT 1')
    lines.append('#define OD_CNT_EM 1')
    lines.append('#define OD_CNT_SYNC 1')
    lines.append('#define OD_CNT_SYNC_PROD 1')
    lines.append('#define OD_CNT_STORAGE 1')
    lines.append('#define OD_CNT_EM_PROD 1')
    lines.append('#define OD_CNT_HB_CONS 1')
    lines.append('#define OD_CNT_HB_PROD 1')
    lines.append('#define OD_CNT_SDO_SRV 1')
    lines.append(f'#define OD_CNT_RPDO {eds.rpdos}')
    lines.append(f'#define OD_CNT_TPDO {eds.tpdos}')
    lines.append('')

    for i in eds.indexes:
        if eds[i].object_type == ObjectType.ARRAY:
            lines.append(f'#define OD_CNT_ARR_{i:X} {len(eds[i]) - 1}')
    lines.append('')

    lines.append('typedef struct {')
    for i in eds.indexes:
        if eds[i].storage_location == StorageLocation.ROM:
            lines += _canopennode_h_lines(eds, i)
    lines.append('} OD_ROM_t;')
    lines.append('')

    lines.append('typedef struct {')
    for i in eds.indexes:
        if eds[i].storage_location == StorageLocation.RAM:
            lines += _canopennode_h_lines(eds, i)
    lines.append('} OD_RAM_t;')
    lines.append('')

    lines.append('typedef struct {')
    for i in eds.indexes:
        if eds[i].storage_location == StorageLocation.PERSIST_COMM:
            lines += _canopennode_h_lines(eds, i)
    lines.append('} OD_PERSIST_COMM_t;')
    lines.append('')

    lines.append('typedef struct {')
    for i in eds.indexes:
        if eds[i].storage_location == StorageLocation.PERSIST_MFR:
            lines += _canopennode_h_lines(eds, i)
    lines.append('} OD_PERSIST_MFR_t;')
    lines.append('')

    lines.append('#ifndef OD_ATTR_ROM')
    lines.append('#define OD_ATTR_ROM')
    lines.append('#endif')
    lines.append('extern OD_ATTR_ROM OD_ROM_t OD_ROM;')
    lines.append('')

    lines.append('#ifndef OD_ATTR_RAM')
    lines.append('#define OD_ATTR_RAM')
    lines.append('#endif')
    lines.append('extern OD_ATTR_RAM OD_RAM_t OD_RAM;')
    lines.append('')

    lines.append('#ifndef OD_ATTR_PERSIST_COMM')
    lines.append('#define OD_ATTR_PERSIST_COMM')
    lines.append('#endif')
    lines.append('extern OD_ATTR_PERSIST_COMM OD_PERSIST_COMM_t OD_PERSIST_COMM;')
    lines.append('')

    lines.append('#ifndef OD_ATTR_PERSIST_MFR')
    lines.append('#define OD_ATTR_PERSIST_MFR')
    lines.append('#endif')
    lines.append('extern OD_ATTR_PERSIST_MFR OD_PERSIST_MFR_t OD_PERSIST_MFR;')
    lines.append('')

    lines.append('#ifndef OD_ATTR_OD')
    lines.append('#define OD_ATTR_OD')
    lines.append('#endif')
    lines.append('extern OD_ATTR_OD OD_t *OD;')
    lines.append('')

    for i in eds.indexes:
        lines.append(f'#define OD_ENTRY_H{i:X} &OD->list[{eds.indexes.index(i)}]')
    lines.append('')

    for i in eds.indexes:
        name = camel_case(eds[i].parameter_name)
        lines.append(f'#define OD_ENTRY_H{i:X}_{name} &OD->list[{eds.indexes.index(i)}]')
    lines.append('')

    lines.append('#endif /* OD_H */')

    with open(file_path, 'w') as f:
        for i in lines:
            f.write(i + '\n')
