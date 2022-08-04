'''All the object class for the object dictionary'''

from . import DataType, AccessType, ObjectType, str2int


class Variable:
    '''Holds EDS variable data'''

    object_type = ObjectType.VAR

    def __init__(self):
        self.comments = ''
        self.parameter_name = ''
        self.denotation = ''
        self.data_type = DataType.UNSIGNED32
        self.low_limit = ''
        self.high_limit = ''
        self.default_value = ''
        self.access_type = AccessType.RW
        self.pdo_mapping = False


class Array:
    '''Holds EDS array data'''

    object_type = ObjectType.ARRAY

    def __init__(self, parameter_name='', subindex0=True):
        '''
        Parameters
        ----------
        parameter_name: str
            Name of the array.
        subindex0: bool
            A flag to auto generate subindex0 (aka subindex for the size of array) for the new
            array.
        '''

        self.parameter_name = parameter_name
        self.denotation = ''
        self.comments = ''
        self._data = {}

        if subindex0:
            var = Variable()
            var.parameter_name = 'Highest sub-index supported'
            var.access_type = AccessType.CONST
            self._data[0] = var

    def __len__(self):
        return len(self._data)

    def __getitem__(self, subindex: int) -> Variable:
        return self._data[subindex]

    def insert(self, subindex: int, variable: Variable, update_subindex0=True) -> None:
        '''Add a subindex to the array'''

        if subindex in self._data:
            raise ValueError('Subindex already exists')

        self._data[subindex] = variable

        # update array size subindex
        if update_subindex0 and 0 in self._data:
            temp = str2int(self._data[0].default_value) + 1
            self._data[0].default_value = f'0x{temp:02X}'

    def remove(self, subindex: int, update_subindex0=True) -> None:
        '''Remove a subindex from the array'''

        if subindex == 0:
            raise ValueError('Cannot remove subindex 0')
        if subindex not in self._data:
            raise ValueError('Subindex does not exist')

        del self._data[subindex]

        # update array size subindex
        if update_subindex0 and 0 in self._data:
            temp = str2int(self._data[0].default_value) - 1
            self._data[0].default_value = f'0x{temp:02X}'

    @property
    def data_type(self) -> DataType:
        '''DataType: Get the data type for all items in array'''
        data_type = None

        # find the first subindex that is not subindex0, if one exist
        if len(self._data) != 0:
            for i in self._data:
                if i != 0:
                    data_type = self._data[i].data_type
                    break

        return data_type

    @data_type.setter
    def data_type(self, data_type: DataType) -> None:
        for i in self._data[1:]:  # skip size subindex
            i.data_type = data_type

    @property
    def subindexes(self) -> list:
        '''Get the list of subindexes'''

        return sorted(self._data.keys())


class Record:
    '''Holds EDS record data'''

    object_type = ObjectType.RECORD

    def __init__(self, parameter_name='', subindex0=True):
        '''
        Parameters
        ----------
        parameter_name: str
            Name of the record.
        subindex0: bool
            A flag to auto generate subindex0 (aka subindex for the size of record).
        '''

        self.parameter_name = parameter_name
        self.denotation = ''
        self.comments = ''
        self._data = {}

        if subindex0:
            var = Variable()
            var.parameter_name = 'Highest sub-index supported'
            var.access_type = AccessType.CONST
            self._data[0] = var

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, subindex: int) -> Variable:
        return self._data[subindex]

    def insert(self, subindex: int, variable: Variable, update_subindex0=True) -> None:
        '''Add a subindex to the record'''

        if subindex in self._data:
            raise ValueError('Subindex already exists')

        self._data[subindex] = variable

        # update record size subindex
        if update_subindex0 and 0 in self._data:
            temp = str2int(self._data[0].default_value) + 1
            self._data[0].default_value = f'0x{temp:02X}'

    def remove(self, subindex: int, update_subindex0=True) -> None:
        '''Remove a subindex from the record'''

        if subindex == 0:
            raise ValueError('Cannot remove subindex 0')
        if subindex not in self._data:
            raise ValueError('Subindex does not exist')

        del self._data[subindex]

        # update record size subindex
        if update_subindex0 and 0 in self._data:
            temp = str2int(self._data[0].default_value) - 1
            self._data[0].default_value = f'0x{temp:02X}'

    @property
    def subindexes(self) -> list:
        '''Get the list of subindexes'''

        return sorted(self._data.keys())
