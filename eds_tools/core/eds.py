import re
from os.path import basename
from collections import UserDict

from . import ObjectType, str2int, DataType
from .eds_format import INDEX_REGEX, SUBINDEX_REGEX, VAR, RECORD_ARRAY, LIST_OBJECTS, COMMENTS, \
    EDS_SECTION_ORDER, MANDATORY_OBJECTS, DEVICE_COMMISSIONING, FILE_INFO, DEVICE_INFO


class EDSSection(UserDict):
    def __init__(self):
        super().__init__({})
        self.header = ''
        self.comment = ''


def new_device_commissioning_section() -> EDSSection:
    section = EDSSection()
    section.header = 'DeviceComissioning'
    for key in DEVICE_COMMISSIONING:
        section[key] = DEVICE_COMMISSIONING[key].default


class EDS:
    def __init__(self):
        self._is_dcf = False
        self._data = {}
        self._file_path = None

    def load(self, file_path: str) -> list:
        '''load an eds/dcf file'''

        self._is_dcf = file_path.endswith('.dcf')
        self._data = {}
        self._file_path = file_path
        errors = []

        with open(file_path, 'r') as fptr:
            raw = fptr.read()

        for section_lines in raw.split('\n\n'):
            if section_lines == '':
                continue  # handle new line at EOF
            errors += self._load_section(section_lines)

        return errors

    def _load_section(self, section_lines) -> list:
        errors = []
        lines = section_lines.split('\n')
        section = EDSSection()

        header_index = [lines.index(i) for i in lines if i.startswith('[')][0]
        header = lines[header_index]
        section.header = header

        for i in lines[:header_index]:
            section.comment += i[1:] + '\n'

        # remove trailing '\n'
        section.comment = section.comment[:-1]

        # read in all seciton keys/values
        raw = {}
        for i in lines[header_index + 1:]:
            key, value = i.split('=')
            raw[key] = value

        header_name = header[1:-1]  # remove '[' and ']'
        if header_name in EDS_SECTION_ORDER:
            definition = EDS_SECTION_ORDER[header_name]
        elif re.match(INDEX_REGEX, header_name):
            if str2int(raw['ObjectType']) == ObjectType.VAR:
                definition = VAR
            elif str2int(raw['ObjectType']) in [ObjectType.ARRAY, ObjectType.RECORD]:
                definition = RECORD_ARRAY
        elif re.match(SUBINDEX_REGEX, header_name):
            definition = VAR
        else:
            raise ValueError('Unknown section: ' + header_name)

        # get all the value for valid EDS keys and log missing ones
        for key in definition:
            try:
                section[key] = definition[key].str2value(raw[key])
            except KeyError:
                if key == 'Denotation':  # always add this even if not dcf
                    if self.is_dcf:
                        errors.append('key "' + key + '" was missing from ' + header)
                    section[key] = definition[key].default
                elif not definition[key].optional:
                    errors.append('key "' + key + '" was missing from ' + header)
                    section[key] = definition[key].default
            except ValueError:
                errors.append('value "' + raw[key] + '" for key "' + key + '" is misformatted')
                section[key] = definition[key].default

        # check for keys from file that are not in EDS definition
        for key in raw:
            if key not in section:
                if definition in [LIST_OBJECTS, COMMENTS]:  # keys are length dependent
                    section[key] = raw[key]
                else:
                    errors.append('unknown key "' + key + '" was in ' + header)

        self._data[header_name] = section

        return errors

    def save(self, file_path: str = None, dcf: bool = False):
        '''Save the eds/dcf file'''
        lines = []

        if not file_path:
            file_path = self._file_path

        # fix name for DCFs
        if dcf and file_path.endswith('.eds'):
            file_path = file_path[:-4] + '.dcf'

        for i in EDS_SECTION_ORDER:
            if i == 'DeviceComissioning' and not dcf:
                continue

            lines.append(self._data[i].header)

            if i in ['FileInfo', 'DeviceInfo', 'DeviceComissioning', 'DummyUsage', 'Comments']:
                for key in self._data[i]:
                    value = EDS_SECTION_ORDER[i][key].value2str(self._data[i][key])
                    if key == 'FileName':
                        value = basename(file_path)
                    lines.append(key + '=' + value)

                lines.append('')
            else:
                key = 'SupportedObjects'
                value = EDS_SECTION_ORDER[i][key].value2str(self._data[i][key])
                lines.append(key + '=' + value)

                if i == 'MandatoryObjects':
                    objects = self.mandatory_objects
                elif i == 'OptionalObjects':
                    objects = self.optional_objects
                elif i == 'ManufacturerObjects':
                    objects = self.manufacturer_objects

                for value in objects:
                    key = str(objects.index(value) + 1)
                    lines.append(key + '=' + value)

                lines.append('')

                lines += self._save_objects(objects, dcf)

        with open(file_path, 'w') as f:
            for i in lines:
                f.write(i + '\n')

    def _save_objects(self, objects: list, dcf: bool) -> list:
        lines = []

        for i in objects:
            section = self.index(i)
            if section.comment:
                for c in section.comment.split('\n'):
                    lines.append(f';{c}')
            lines.append(section.header)
            name = section.header[1:-1]

            for key in self._data[name]:
                if key == 'Denotation' and dcf is False:
                    continue  # Denotation is for DCF only
                if self._data[name]['ObjectType'] == ObjectType.VAR:
                    value = VAR[key].value2str(self._data[name][key])
                else:
                    value = RECORD_ARRAY[key].value2str(self._data[name][key])
                lines.append(key + '=' + value)

            lines.append('')

            for j in self.subindexes(i):
                section = self.subindex(i, j)
                if section.comment:
                    for c in section.comment.split('\n'):
                        lines.append(f';{c}')
                lines.append(section.header)
                name = section.header[1:-1]

                for key in self._data[name]:
                    if key == 'Denotation' and dcf is False:
                        continue  # Denotation is for DCF only
                    value = VAR[key].value2str(self._data[name][key])
                    lines.append(key + '=' + value)

                lines.append('')

        return lines

    def _is_valid_section(self, section: EDSSection, header: str, definition: dict) -> bool:
        if section.header != header:
            raise ValueError(f'device commissioning header not "{header}"')

        for i in definition:
            if i not in section:
                raise ValueError(f'missing key "{i}"')
            if not definition[i].is_valid(section[i]):
                raise TypeError(f'invalid type for key "{i}"')

        for i in section:
            if i not in definition:
                raise ValueError(f'unknown key "{i}"')

    @property
    def file_info(self) -> EDSSection:
        '''Get the section for file info'''
        return self._data['FileInfo'].copy()

    @file_info.setter
    def file_info(self, section: EDSSection):
        '''Set the section for file info'''
        self._is_valid_section(section, '[FileInfo]', FILE_INFO)
        self._data['FileInfo'] = section

    @property
    def device_info(self) -> EDSSection:
        '''Get the device info section of the eds'''
        return self._data['DeviceInfo'].copy()

    @device_info.setter
    def device_info(self, section: EDSSection):
        '''Set the section for device info'''
        self._is_valid_section(section, '[DeviceInfo]', DEVICE_INFO)
        self._data['DeviceInfo'] = section

    @property
    def mandatory_objects(self) -> list:
        '''Get the list of all mandatory objects in OD'''
        mandatory_objects = []

        for i in MANDATORY_OBJECTS:
            if i[2:] in self._data:
                mandatory_objects.append(i)

        return mandatory_objects

    @property
    def optional_objects(self) -> list:
        '''Get the list of all optional objects in OD'''
        optional_objects = []

        for i in self._data:
            if not re.match(INDEX_REGEX, i):
                continue

            i_hex = '0x' + i
            if i_hex in MANDATORY_OBJECTS:
                continue

            index = str2int(i_hex)
            if (index >= 0x1000 and index <= 0x1FFF) or (index >= 0x6000 and index <= 0XFFFF):
                optional_objects.append(i_hex)

        return optional_objects

    @property
    def manufacturer_objects(self) -> list:
        '''Get the list of all manufacturer objects in OD'''
        manufacturer_objects = []

        for i in self._data:
            if not re.match(INDEX_REGEX, i):
                continue

            i_hex = '0x' + i
            if i in MANDATORY_OBJECTS:
                continue

            index = str2int(i_hex)
            if index >= 0x2000 and index <= 0x5FFF:
                manufacturer_objects.append(i_hex)

        return manufacturer_objects

    @property
    def device_commissioning(self) -> EDSSection:
        '''EDSSection: Get the section for device commissioning (DCF only)'''
        data = None

        if 'DeviceComissioning' in self._data:
            data = self._data['DeviceComissioning'].copy

        return data

    @device_commissioning.setter
    def device_commissioning(self, section: EDSSection):
        '''Set the section for device commissioning (DCF only)'''
        self._is_valid_section(section, '[DeviceComissioning]', DEVICE_COMMISSIONING)
        self._data['DeviceComissioning'] = section
        self._is_dcf = True

    def indexes(self) -> list:
        '''Get the list of indexes'''
        indexes = []

        for i in self._data:
            if re.match(INDEX_REGEX, i):
                indexes.append(int(i, 16))

        # sort the indexes before returning
        return [f'0x{i:X}' for i in sorted(indexes)]

    def subindexes(self, index: str) -> list:
        '''Get the list of subindexes for an index'''
        subindexes = []

        temp = index[2:] + 'sub'

        for i in self._data:
            if i.startswith(temp):
                subindexes.append('0x' + i[7:])

        return subindexes

    def index(self, index: str) -> EDSSection:
        '''Get a copy of the section data at an index'''
        key = index[2:]
        data = self._data[key].copy()
        return data

    def subindex(self, index: str, subindex: str) -> EDSSection:
        '''Get a copy of the section data at an subindex'''
        key = index[2:] + 'sub' + subindex[2:]
        data = self._data[key].copy()
        return data

    def add_variable_index(self, index: int):
        '''Add a new VAR index to OD'''
        key = hex(index)[2:]
        if key in self._data:
            raise ValueError('Index already exist')

        eds_section = EDSSection()
        for i in VAR:
            eds_section[i] = VAR[i].default
        self._data[key] = eds_section

    def add_variable_subindex(self, index: int, subindex: int):
        '''Add a new subindex to OD'''
        key = hex(index)[2:] + 'sub' + hex(subindex)[2:]
        if key in self._data:
            raise ValueError('Subindex already exist')

        eds_section = EDSSection()
        for i in VAR:
            eds_section[i] = VAR[i].default
        self._data[key] = eds_section

    def add_record(self, index: int):
        '''Add a new record to OD'''
        key = hex(index)[2:]
        if key in self._data:
            raise ValueError('Index already exist')

        # add record index
        eds_section = EDSSection()
        for i in RECORD_ARRAY:
            eds_section[i] = RECORD_ARRAY[i].default
        eds_section['SubNumber'] = '0x01'
        self._data[key] = eds_section

        # add subindex 0
        eds_section = EDSSection()
        for i in VAR:
            eds_section[i] = VAR[i].default
        eds_section['ParameterName'] = 'Highest sub-index supported'
        eds_section['DataType'] = DataType.UNSIGNED8
        eds_section['AccessType'] = 'ro'
        eds_section['DefaultValue'] = '0x00'
        key = hex(index)[2:] + 'sub0'
        self._data[key] = eds_section

    def add_array(self, index: int, size: int, data_type: DataType):
        '''Add a new array to OD'''
        key = hex(index)[2:]
        if key in self._data:
            raise ValueError('Index already exist')

        # add array index
        eds_section = EDSSection()
        for i in RECORD_ARRAY:
            eds_section[i] = RECORD_ARRAY[i].default
        eds_section['SubNumber'] = hex(index)
        self._data[key] = eds_section

        # add subindex 0
        eds_section = EDSSection()
        for i in VAR:
            eds_section[i] = VAR[i].default
        eds_section['ParameterName'] = 'Highest sub-index supported'
        eds_section['DataType'] = DataType.UNSIGNED8
        eds_section['AccessType'] = 'ro'
        eds_section['DefaultValue'] = '0x00'
        key = hex(index)[2:] + 'sub0'
        self._data[key] = eds_section

        # add subindexes
        for i in size:
            eds_section = EDSSection()
            for i in VAR:
                eds_section[i] = VAR[i].default
            eds_section['ParameterName'] = 'Highest sub-index supported'
            eds_section['DataType'] = data_type
            eds_section['DefaultValue'] = '0'
            key = hex(index)[2:] + 'sub' + hex(size + 1)[2:]
            self._data[key] = eds_section

    def remove_index(self, index: int):
        '''Remove a index from the OD'''
        name = hex(index)[2:]

        if name in self._data:
            if self._data[name]['ObjectType'] != ObjectType.VAR:  # delete all the subindexes
                for i in self.subindexes():
                    del self._data[i[2:]]
            del self._data[name]

    def remove_subindex(self, index: int, subindex: int):
        '''Remove a subindex from the OD'''
        name = hex(index)[2:]
        sub_name = hex(index)[2:] + 'sub' + hex(subindex)[2:]
        del self._data[sub_name]

        # decress the subindex count for the reocord/array
        temp = str2int(self._data[name]['DefaultValue'])
        temp -= 12
        self._data[name]['DefaultValue'] = hex(temp)

    @property
    def is_dcf(self):
        '''Check if the file that was loaded is a dcf or not'''
        return self._is_dcf

    def update_object(self, obj: EDSSection):
        '''update a object in the OD'''
        pass
