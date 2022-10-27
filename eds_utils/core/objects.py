'''All the object class for the object dictionary'''

from . import DataType, AccessType, ObjectType, StorageLocation


class Variable:
    '''Holds EDS variable data'''

    def __init__(self, parameter_name='New Variable'):
        '''
        Parameters
        ----------
        parameter_name: str
            Name of the new variable.
        '''

        self.comments = ''
        self.parameter_name = parameter_name
        self.denotation = ''
        self.data_type = DataType.UNSIGNED32
        self.low_limit = ''
        self.high_limit = ''
        self.default_value = ''
        self.access_type = AccessType.RW
        self.pdo_mapping = False
        self.object_type = ObjectType.VAR
        self.storage_location = StorageLocation.RAM  # for CANopenNode support


class Record:
    '''Holds EDS record data'''

    def __init__(self, parameter_name='New Record'):
        '''
        Parameters
        ----------
        parameter_name: str
            Name of the new record.
        '''

        self.parameter_name = parameter_name
        self.denotation = ''
        self.comments = ''
        self._data = {}
        self.object_type = ObjectType.RECORD
        self._storage_location = StorageLocation.RAM  # for CANopenNode support

        var = Variable()
        var.parameter_name = 'Highest sub-index supported'
        var.access_type = AccessType.CONST
        var.data_type = DataType.UNSIGNED8
        var.default_value = '0x00'
        self._data[0] = var

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, subindex: int) -> Variable:
        return self._data[subindex]

    def __setitem__(self, subindex: int, variable: Variable):
        '''Add a subindex to the record'''

        if subindex == 0:  # overwrite entries in subindex 0
            self._data[subindex].parameter_name = variable.parameter_name
            self._data[subindex].access_type = variable.access_type
        elif subindex in self._data:  # add subindex
            raise ValueError('Subindex already exists')
        else:
            self._data[subindex] = variable

            # update record size subindex
            self._data[0].default_value = f'0x{len(self._data) - 1:02X}'

    def __delitem__(self, subindex: int):
        '''Remove a subindex from the record'''

        if subindex == 0:
            raise ValueError('Cannot remove subindex 0')
        if subindex not in self._data:
            raise ValueError('Subindex does not exist')

        del self._data[subindex]

        # update record size subindex
        self._data[0].default_value = f'0x{len(self._data) - 1:02X}'

    @property
    def subindexes(self) -> list:
        '''Get the list of subindexes'''

        return sorted(self._data.keys())

    @property
    def storage_location(self) -> StorageLocation:
        '''The storage location of object'''

        return self._storage_location

    @storage_location.setter
    def storage_location(self, storage_location: StorageLocation):

        for i in self._data:
            self._data[i].storage_location = storage_location

        self._storage_location = storage_location


class Array(Record):
    '''Holds EDS array data'''

    def __init__(self, parameter_name='New Array'):
        '''
        Parameters
        ----------
        parameter_name: str
            Name of the new array.
        '''

        super().__init__(parameter_name)
        self.object_type = ObjectType.ARRAY
        self._data_type = None

    def __setitem__(self, subindex: int, variable: Variable):
        '''Add a subindex to the array'''

        if subindex == 0:  # overwrite entries in subindex 0
            self._data[subindex].parameter_name = variable.parameter_name
            self._data[subindex].access_type = variable.access_type
        elif subindex in self._data:  # add subindex
            raise ValueError('Subindex already exists')
        elif self._data_type and variable.data_type != self._data_type:
            raise ValueError('Variable\'s data type does not match array\'s data type')
        else:
            self._data[subindex] = variable

            # update record size subindex
            self._data[0].default_value = f'0x{len(self._data) - 1:02X}'

    @property
    def data_type(self) -> DataType:
        '''DataType: Get the data type for all items in array'''
        return self._data_type

    @data_type.setter
    def data_type(self, data_type: DataType):
        self._data_type = data_type

        for i in self._data:
            if i != 0:
                self._data[i].data_type = data_type
