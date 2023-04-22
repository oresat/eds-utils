'''All the object class for the object dictionary'''

from dataclasses import dataclass
from typing import List

from . import DataType, AccessType, ObjectType


@dataclass
class Variable:
    '''Holds EDS variable data'''

    comments: str = ''
    parameter_name: str = 'New Variable'
    denotation: str = ''
    data_type: DataType = DataType.UNSIGNED32
    low_limit: str = ''
    high_limit: str = ''
    default_value: str = ''
    access_type: AccessType = AccessType.RW
    pdo_mapping: bool = False
    object_type: ObjectType = ObjectType.VAR
    storage_location: str = ''  # for CANopenNode support

    def __hash__(self):
        return hash((self.parameter_name, self.data_type, self.comments))


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
        self.object_type = ObjectType.RECORD
        self._storage_location = ''  # for CANopenNode support
        self._data = {
            0: Variable(
                parameter_name='Highest sub-index supported',
                access_type=AccessType.CONST,
                data_type=DataType.UNSIGNED8,
                default_value='0x00'
            )
        }

    def __eq__(self, other) -> bool:

        if self.parameter_name != other.parameter_name:
            return False
        if self.denotation != other.denotation:
            return False
        if self.comments != other.comments:
            return False
        if self.object_type != other.object_type:
            return False
        if self.storage_location != other.storage_location:
            return False
        if self.subindexes != other.subindexes:
            return False

        for subindex in self.subindexes:
            if self[subindex] != other[subindex]:
                return False

        return True

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
            variable.storage_location = self.storage_location
            self._data[subindex] = variable

            # make sure the subindexes are ordered
            self._data = dict(sorted(self._data.items()))

            # update record highest subindex
            self._data[0].default_value = f'0x{list(self._data)[-1]:02X}'

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
    def subindexes(self) -> List[int]:
        '''Get the list of subindexes'''

        return list(self._data.keys())

    @property
    def storage_location(self) -> str:
        '''The storage location of object'''

        return self._storage_location

    @storage_location.setter
    def storage_location(self, storage_location: str):

        for i in self._data:
            self._data[i].storage_location = storage_location

        self._storage_location = storage_location


class Array(Record):
    '''Holds EDS array data'''

    def __init__(self, parameter_name='New Array', data_type: DataType = None):
        '''
        Parameters
        ----------
        parameter_name: str
            Name of the new array.
        data_type: DataType
            The data type for the array. Can None if not determind yet.
        '''

        super().__init__(parameter_name)
        self.object_type = ObjectType.ARRAY
        self._data_type = data_type

    def __eq__(self, other) -> bool:

        if not super().__eq__(other):
            return False

        if self.data_type != other.data_type:
            return False

        return True

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
            variable.storage_location = self.storage_location
            self._data[subindex] = variable

            # set the data_type if not set
            if not self._data_type:
                self._data_type = variable.data_type

            # make sure the subindexes are ordered
            self._data = dict(sorted(self._data.items()))

            # update record highest subindex
            self._data[0].default_value = f'0x{list(self._data)[-1]:02X}'

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
