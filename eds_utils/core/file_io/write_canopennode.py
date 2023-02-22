'''Everything to write an eds/dcf as CANopenNode OD.[c/h] files'''

import math as m

from . import INDENT4, INDENT8, INDENT12
from .. import ObjectType, DataType, AccessType
from ..eds import EDS
from ..objects import Variable

_SKIP_INDEXES = [0x1F81, 0x1F82, 0x1F89]
'''CANopenNode skips the data (it just set to NULL) for these indexes for some reason'''

DATA_TYPE_STR = [
    DataType.VISIBLE_STRING,
    DataType.UNICODE_STRING,
]

DATA_TYPE_C_TYPES = {
    DataType.BOOLEAN: 'bool_t',
    DataType.INTEGER8: 'int8_t',
    DataType.INTEGER16: 'int16_t',
    DataType.INTEGER32: 'int32_t',
    DataType.UNSIGNED8: 'uint8_t',
    DataType.UNSIGNED16: 'uint16_t',
    DataType.UNSIGNED32: 'uint32_t',
    DataType.REAL32: 'float',
    DataType.VISIBLE_STRING: 'char',
    DataType.OCTET_STRING: 'uint8_t',
    DataType.UNICODE_STRING: 'uint16_t',
    DataType.DOMAIN: None,
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

    if default_value == '':
        return '0'
    elif len(temp) == 1:
        return default_value  # does not include $NODEID
    elif temp[0] == '$NODEID':
        return temp[1].rsplit()[0]
    elif temp[1] == '$NODEID':
        return temp[0].rsplit()[0]

    return default_value  # does not include $NODEID


def attr_lines(eds: EDS, index: int) -> list:
    '''Generate attr lines for OD.c for a sepecific index'''

    lines = []

    obj = eds[index]
    if obj.object_type == ObjectType.VAR:
        default_value = remove_node_id(obj.default_value)
        line = f'{INDENT4}.x{index:X}_{camel_case(obj.parameter_name)} = '

        if obj.data_type == DataType.VISIBLE_STRING:
            line += '{'
            for i in obj.default_value:
                line += f'\'{i}\', '
            line += '0}, '
        elif obj.data_type == DataType.OCTET_STRING:
            line += '{'
            value = obj.default_value.replace('  ', ' ')
            for i in value.split(' '):
                line += f'0x{i}, '
            line = line[:-2]  # remove last ', '
            line += '},'
        elif obj.data_type == DataType.UNICODE_STRING:
            line += '{'
            for i in obj.default_value:
                line += f'0x{ord(i):04X}, '
            line += f'0x{0:04X}'  # add the '\0'
            line += '},'
        else:
            line += f'{default_value},'

        if index not in _SKIP_INDEXES:
            lines.append(line)
    elif obj.object_type == ObjectType.ARRAY:
        name = camel_case(obj.parameter_name)
        lines.append(f'{INDENT4}.x{index:X}_{name}_sub0 = {obj[0].default_value},')
        line = f'{INDENT4}.x{index:X}_{name} = ' + '{'

        if obj.data_type == DataType.DOMAIN:
            return lines  # skip domains

        for i in obj.subindexes[1:]:
            default_value = remove_node_id(obj[i].default_value)

            if obj[i].data_type == DataType.VISIBLE_STRING:
                line += '{'
                for i in obj[i].default_value:
                    line += f'\'{i}\', '
                line += '0}, '
            elif obj[i].data_type == DataType.OCTET_STRING:
                line += '{'
                value = obj[i].default_value.replace('  ', ' ')
                for i in value.split(' '):
                    line += f'0x{i}, '
                line = line[:-2]  # remove trailing ', '
                line += '}, '
            elif obj[i].data_type == DataType.UNICODE_STRING:
                line += '{'
                for i in obj[i].default_value:
                    line += f'0x{ord(i):04X}, '
                line += f'0x{0:04X}'  # add the '\0'
                line += '}, '
            else:
                line += f'{default_value}, '

        line = line[:-2]  # remove trailing ', '
        line += '},'

        if index not in _SKIP_INDEXES:
            lines.append(line)
    else:  # ObjectType.Record
        lines.append(f'{INDENT4}.x{index:X}_{camel_case(obj.parameter_name)} = ' + '{')

        for i in obj.subindexes:
            name = camel_case(obj[i].parameter_name)
            default_value = remove_node_id(obj[i].default_value)

            if obj[i].data_type == DataType.DOMAIN:
                continue  # skip domains
            elif obj[i].data_type == DataType.VISIBLE_STRING:
                line = f'{INDENT8}.{name} = ' + '{'
                for i in obj[i].default_value:
                    line += f'\'{i}\', '
                line += '0}, '
                lines.append(line)
            elif obj[i].data_type == DataType.OCTET_STRING:
                value = obj[i].default_value.replace('  ', ' ')
                line = f'{INDENT8}.{name} = ' + '{'
                for i in value.split(' '):
                    line += f'0x{i}, '
                line = line[:-2]  # remove trailing ', '
                line += '},'
                lines.append(line)
            elif obj[i].data_type == DataType.UNICODE_STRING:
                line = f'{INDENT8}.{name} = ' + '{'
                for i in obj[i].default_value:
                    line += f'0x{ord(i):04X}, '
                line += f'0x{0:04X}'  # add the '\0'
                line += '},'
                lines.append(line)
            else:
                lines.append(f'{INDENT8}.{name} = {default_value},')

        lines.append(INDENT4 + '},')

    return lines


def _var_data_type_len(var: Variable) -> int:
    '''Get the length of the variable's data in bytes'''

    if var.data_type == DataType.VISIBLE_STRING:
        length = len(var.default_value)  # char
    elif var.data_type == DataType.OCTET_STRING:
        length = len(var.default_value.replace(' ', '')) // 2
    elif var.data_type == DataType.UNICODE_STRING:
        length = len(var.default_value) * 2  # uint16_t
    else:
        length = var.data_type.size // 8

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

    if var.data_type in DATA_TYPE_STR:
        attr_str += ' | ODA_STR'
    elif (var.data_type.size // 8) > 1:
        attr_str += ' | ODA_MB'

    return attr_str


def obj_lines(eds: EDS, index) -> list:
    '''Generate object lines for OD.c for a sepecific index'''

    lines = []

    obj = eds[index]
    name = camel_case(obj.parameter_name)
    lines.append(f'{INDENT4}.o_{index:X}_{name} = ' + '{')

    if obj.object_type == ObjectType.VAR:
        st_loc = obj.storage_location

        if index in _SKIP_INDEXES or obj.data_type == DataType.DOMAIN:
            lines.append(f'{INDENT8}.dataOrig = NULL,')
        elif obj.data_type in DATA_TYPE_STR or obj.data_type == DataType.OCTET_STRING:
            lines.append(f'{INDENT8}.dataOrig = &OD_{st_loc}.x{index:X}_{name}[0],')
        else:
            lines.append(f'{INDENT8}.dataOrig = &OD_{st_loc}.x{index:X}_{name},')

        lines.append(f'{INDENT8}.attribute = {_var_attr_flags(obj)},')
        lines.append(f'{INDENT8}.dataLength = {_var_data_type_len(obj)}')
    elif obj.object_type == ObjectType.ARRAY:
        st_loc = obj.storage_location

        lines.append(f'{INDENT8}.dataOrig0 = &OD_{st_loc}.x{index:X}_{name}_sub0,')

        if index in _SKIP_INDEXES or obj.data_type == DataType.DOMAIN:
            lines.append(f'{INDENT8}.dataOrig = NULL,')
        elif obj.data_type in [DataType.VISIBLE_STRING, DataType.OCTET_STRING,
                               DataType.UNICODE_STRING]:
            lines.append(f'{INDENT8}.dataOrig = &OD_{st_loc}.x{index:X}_{name}[0][0],')
        else:
            lines.append(f'{INDENT8}.dataOrig = &OD_{st_loc}.x{index:X}_{name}[0],')

        lines.append(f'{INDENT8}.attribute0 = ODA_SDO_R,')
        lines.append(f'{INDENT8}.attribute = {_var_attr_flags(obj[1])},')
        length = _var_data_type_len(obj[1])
        lines.append(f'{INDENT8}.dataElementLength = {length},')

        c_name = DATA_TYPE_C_TYPES[obj.data_type]
        if obj.data_type == DataType.DOMAIN:
            lines.append(f'{INDENT8}.dataElementSizeof = 0,')
        elif obj.data_type in DATA_TYPE_STR:
            sub_length = len(obj[1].default_value) + 1  # add 1 for '\0'
            lines.append(f'{INDENT8}.dataElementSizeof = sizeof({c_name}[{sub_length}]),')
        elif obj.data_type == DataType.OCTET_STRING:
            sub_length = m.ceil(len(obj[1].default_value.replace(' ', '')) / 2)
            lines.append(f'{INDENT8}.dataElementSizeof = sizeof({c_name}[{sub_length}]),')
        else:
            lines.append(f'{INDENT8}.dataElementSizeof = sizeof({c_name}),')
    else:  # ObjectType.DOMAIN
        for i in obj.subindexes:
            st_loc = obj.storage_location
            name_sub = camel_case(obj[i].parameter_name)
            lines.append(INDENT8 + '{')

            if obj[i].data_type == DataType.DOMAIN:
                lines.append(f'{INDENT12}.dataOrig = NULL,')
            elif obj[i].data_type in [DataType.VISIBLE_STRING, DataType.OCTET_STRING,
                                      DataType.UNICODE_STRING]:
                line = f'{INDENT12}.dataOrig = &OD_{st_loc}.x{index:X}_{name}.{name_sub}[0],'
                lines.append(line)
            else:
                lines.append(f'{INDENT12}.dataOrig = &OD_{st_loc}.x{index:X}_{name}.{name_sub},')

            lines.append(f'{INDENT12}.subIndex = {i},')
            lines.append(f'{INDENT12}.attribute = {_var_attr_flags(obj[i])},')
            lines.append(f'{INDENT12}.dataLength = {_var_data_type_len(obj[i])}')
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

    for i in eds.storage_locations:
        sl = i.upper().replace('-', '_')
        lines.append(f'OD_ATTR_{sl} OD_{sl}_t OD_{sl} = ' + '{')
        for j in eds.indexes:
            if eds[j].storage_location == i:
                lines += attr_lines(eds, j)
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

        if obj.data_type == DataType.DOMAIN:
            pass  # skip domains
        elif obj.data_type in DATA_TYPE_STR:
            length = len(obj.default_value) + 1  # add 1 for '\0'
            lines.append(f'{INDENT4}{c_name} x{index:X}_{name}[{length}];')
        elif obj.data_type == DataType.OCTET_STRING:
            length = len(obj.default_value.replace(' ', '')) // 2  # aka number of uint8s
            lines.append(f'{INDENT4}{c_name} x{index:X}_{name}[{length}];')
        else:
            lines.append(f'{INDENT4}{c_name} x{index:X}_{name};')
    elif obj.object_type == ObjectType.ARRAY:
        c_name = DATA_TYPE_C_TYPES[obj.data_type]
        length = f'OD_CNT_ARR_{index:X}'
        lines.append(f'{INDENT4}uint8_t x{index:X}_{name}_sub0;')

        if obj.data_type == DataType.DOMAIN:
            pass  # skip domains
        elif index in _SKIP_INDEXES:
            pass
        elif obj.data_type in DATA_TYPE_STR:
            sub_length = len(obj[1].default_value) + 1  # add 1 for '\0'
            lines.append(f'{INDENT4}{c_name} x{index:X}_{name}[{length}][{sub_length}];')
        elif obj.data_type == DataType.OCTET_STRING:
            sub_length = m.ceil(len(obj[1].default_value.replace(' ', '')) / 2)
            lines.append(f'{INDENT4}{c_name} x{index:X}_{name}[{length}][{sub_length}];')
        else:
            lines.append(f'{INDENT4}{c_name} x{index:X}_{name}[{length}];')
    else:
        lines.append(INDENT4 + 'struct {')
        for i in obj.subindexes:
            data_type = obj[i].data_type
            c_name = DATA_TYPE_C_TYPES[data_type]
            sub_name = camel_case(obj[i].parameter_name)

            if data_type == DataType.DOMAIN:
                continue  # skip domains
            elif data_type in DATA_TYPE_STR:
                length = len(obj[i].default_value) + 1  # add 1 for '\0'
                lines.append(f'{INDENT8}{c_name} {sub_name}[{length}];')
            elif data_type == DataType.OCTET_STRING:
                sub_length = m.ceil(len(obj[1].default_value.replace(' ', '')) / 2)
                lines.append(f'{INDENT8}{c_name} {sub_name}[{sub_length}];')
            else:
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
    if 0x1280 in eds.indexes:
        lines.append('#define OD_CNT_SDO_CLI 1')
    lines.append(f'#define OD_CNT_RPDO {eds.rpdos}')
    lines.append(f'#define OD_CNT_TPDO {eds.tpdos}')
    lines.append('')

    for i in eds.indexes:
        if eds[i].object_type == ObjectType.ARRAY:
            lines.append(f'#define OD_CNT_ARR_{i:X} {len(eds[i]) - 1}')
    lines.append('')

    for i in eds.storage_locations:
        sl = i.upper().replace('-', '_')
        lines.append('typedef struct {')
        for j in eds.indexes:
            if eds[j].storage_location == i:
                lines += _canopennode_h_lines(eds, j)
        lines.append('}' + f' OD_{sl}_t;')
        lines.append('')

    for i in eds.storage_locations:
        sl = i.upper().replace('-', '_')
        lines.append(f'#ifndef OD_ATTR_{sl}')
        lines.append(f'#define OD_ATTR_{sl}')
        lines.append('#endif')
        lines.append(f'extern OD_ATTR_{sl} OD_{sl}_t OD_{sl};')
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
