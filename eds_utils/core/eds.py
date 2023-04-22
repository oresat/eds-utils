from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List
from copy import deepcopy

from . import DataType
from .objects import Variable, Record


class EDSError(Exception):
    '''Error with EDS'''


@dataclass
class FileInfo:

    file_name: str = 'new_file.eds'
    file_version: int = 0
    file_revision: int = 0
    last_eds: int = ''  # DCF only
    eds_version: str = '4.0'
    description: str = ''
    creation_dt: datetime = datetime.now()
    created_by: str = ''
    modification_dt: datetime = datetime.now()
    modified_by: str = ''

    def __eq__(self, other) -> bool:
        # ignore file_name, modification_dt, and modified_by

        if self.file_version != other.file_version \
                or self.file_revision != other.file_revision \
                or self.description != other.description \
                or self.creation_dt != other.creation_dt \
                or self.created_by != other.created_by:
            return False

        return True


@dataclass
class DeviceInfo:

    vendor_name: str = ''
    vendor_number: int = 0
    product_name: str = ''
    product_number: int = 0
    revision_number: int = 0
    order_code: int = ''
    baud_rate: Dict[int, bool] = field(default_factory=lambda: ({
        10: True,
        20: True,
        50: True,
        125: True,
        250: True,
        500: True,
        800: True,
        1000: True,
    }))
    simple_boot_up_master: bool = False
    simple_boot_up_slave: bool = False
    grandularity: int = 8
    dynamic_channel_supperted: bool = False
    group_messaging: bool = False
    num_of_rpdo: int = 0
    num_of_tpdo: int = 0
    lss_supported: bool = False

    def __eq__(self, other) -> bool:
        if self.vendor_name != other.vendor_name \
                or self.vendor_number != other.vendor_number \
                or self.product_name != other.product_name \
                or self.product_number != other.product_number \
                or self.order_code != other.order_code \
                or self.baud_rate != other.baud_rate \
                or self.simple_boot_up_master != other.simple_boot_up_master \
                or self.simple_boot_up_slave != other.simple_boot_up_slave \
                or self.grandularity != other.grandularity \
                or self.dynamic_channel_supperted != other.dynamic_channel_supperted \
                or self.group_messaging != other.group_messaging \
                or self.num_of_rpdo != other.num_of_rpdo \
                or self.num_of_tpdo != other.num_of_tpdo \
                or self.lss_supported != other.lss_supported:
            return False

        return True


@dataclass
class DeviceCommissioning:

    node_id: int = 1
    node_name: str = ''
    baud_rate: int = 1000
    net_number: int = 0
    network_name: str = ''
    canopen_manager: bool = False
    lss_serialnumber: int = 0

    def __eq__(self, other) -> bool:
        if self.node_id != other.node_id \
                or self.node_name != other.node_name \
                or self.baud_rate != other.baud_rate \
                or self.net_number != other.net_number \
                or self.network_name != other.network_name \
                or self.canopen_manager != other.canopen_manager \
                or self.lss_serialnumber != other.lss_serialnumber:
            return False

        return True


class EDS:

    RPDO_COMM_START = 0x1400
    RPDO_COMM_END = RPDO_COMM_START + 0x200

    RPDO_PARA_START = 0x1600
    RPDO_PARA_END = RPDO_PARA_START + 0x200

    TPDO_COMM_START = 0x1800
    TPDO_COMM_END = TPDO_COMM_START + 0x200

    TPDO_PARA_START = 0x1A00
    TPDO_PARA_END = TPDO_PARA_START + 0x200

    MANDATORY_OBJECTS = [0x1000, 0x1001, 0x1018]

    def __init__(self):

        self._data = {}
        self.file_info = FileInfo()
        self.device_info = DeviceInfo()
        self.device_commissioning = DeviceCommissioning()
        self.comment = ''
        self.canopennode = False  # flag for canopennode eds/dcf
        self._storage_locations = []

    def __eq__(self, other) -> bool:
        if self.indexes != other.indexes \
                or self.file_info != other.file_info \
                or self.device_info != other.device_info \
                or self.device_commissioning != other.device_commissioning \
                or self.comment != other.comment \
                or self.canopennode != other.canopennode:
            return False

        for i in self.indexes:
            if self[i] != other[i]:
                return False

        return True

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, index: int, item):
        if index in self._data:
            raise EDSError(f'index 0x{index:X} already exist')

        if item.storage_location == '' and self._storage_locations:
            item.storage_location = self._storage_locations[0]

        self._data[index] = item

        self._data = dict(sorted(self._data.items()))

    def __delitem__(self, index: int):
        del self._data[index]

    def insert(self, index: int, subindex: int, item):
        '''Insert a object into the object dictionary'''

        if subindex is None:
            if index in self._data:
                raise EDSError(f'index 0x{index:X} already exist')
            self._data[index] = item
        elif index not in self._data:
            raise EDSError(f'cannot insert subindex 0x{subindex:X} for index 0x{index:X}, as that '
                           'index does not exist')
        elif isinstance(self._data[index], Variable):
            raise EDSError('cannot insert a subindex into a Variable')
        elif subindex in self._data[index].subindexes:
            raise EDSError(f'subindex 0x{subindex:X} already exist for index 0x{index:X}')
        elif not isinstance(item, Variable):
            raise EDSError('cannot insert non-Variable into subindex')
        else:
            self._data[index][subindex] = item

    def remove(self, index: int, subindex: int = None):
        '''Remove a object from the object dictionary'''

        if subindex is None:  # use only index
            del self._data[index]
        else:  # use index and subindex
            del self._data[index][subindex]

    def add_rpdo(self):
        '''Add RPDO to the object dictionary'''

        # find next rpdo splot
        next_rpdo = -1
        for i in range(self.RPDO_COMM_START, self.RPDO_PARA_START):
            if i not in self._data:
                next_rpdo = i - self.RPDO_COMM_START
                break

        if next_rpdo == -1:
            raise EDSError('No more RPDO slots')

        temp = next_rpdo % 4
        if temp == 0:
            cob_id = '$NODEID + 0x200'
        elif temp == 1:
            cob_id = '$NODEID + 0x300'
        elif temp == 2:
            cob_id = '$NODEID + 0x400'
        else:  # 3
            cob_id = '$NODEID + 0x500'

        # communication object
        comm_rec = Record('RPDO communication parameter')
        comm_rec[1] = Variable(parameter_name='COB-ID used by RPDO', default_value=cob_id)
        comm_rec[2] = Variable(parameter_name='Transmission type')
        comm_rec[3] = Variable(parameter_name='Inhibit time')
        # subindex 4 is reserved in CiA 301
        comm_rec[5] = Variable(parameter_name='Event timer')
        comm_rec[6] = Variable(parameter_name='SYNC start value', data_type=DataType.UNSIGNED8)
        self._data[self.RPDO_COMM_START + next_rpdo] = comm_rec

        # mapping object
        para_rec = Record('RPDO mapping parameter')
        for i in range(1, 9):
            para_rec[i] = Variable(parameter_name=f'Application object {i}')
        self._data[self.RPDO_PARA_START + next_rpdo] = para_rec

    def add_tpdo(self):
        '''Add TPDO to the object dictionary'''

        # find next tpdo splot
        next_tpdo = -1
        for i in range(self.TPDO_COMM_START, self.TPDO_PARA_START):
            if i not in self._data:
                next_tpdo = i - self.TPDO_COMM_START
                break

        if next_tpdo == -1:
            raise EDSError('No more TPDO slots')

        temp = next_tpdo % 4
        if temp == 0:
            cob_id = '$NODEID + 0x180'
        elif temp == 1:
            cob_id = '$NODEID + 0x280'
        elif temp == 2:
            cob_id = '$NODEID + 0x380'
        else:  # 3
            cob_id = '$NODEID + 0x480'

        # communication object
        comm_rec = Record('TPDO communication parameter')
        comm_rec[1] = Variable(parameter_name='COB-ID used by TPDO', default_value=cob_id)
        comm_rec[2] = Variable(parameter_name='Transmission type')
        comm_rec[3] = Variable(parameter_name='Inhibit time')
        # subindex 4 is reserved in CiA 301
        comm_rec[5] = Variable(parameter_name='Event timer')
        comm_rec[6] = Variable(parameter_name='SYNC start value', data_type=DataType.UNSIGNED8)
        self._data[self.TPDO_COMM_START + next_tpdo] = comm_rec

        # mapping object
        para_rec = Record('TPDO mapping parameter')
        for i in range(1, 9):
            para_rec[i] = Variable(parameter_name=f'Application object {i}')
        self._data[self.TPDO_PARA_START + next_tpdo] = para_rec

    @property
    def rpdos(self) -> int:
        '''int: The number of RPDOs'''

        count = 0
        for i in range(self.RPDO_COMM_START, self.RPDO_PARA_START):
            if i in self._data:
                count += 1

        return count

    @property
    def tpdos(self) -> int:
        '''int: The number of TPDOs'''

        count = 0
        for i in range(self.TPDO_COMM_START, self.TPDO_PARA_START):
            if i in self._data:
                count += 1

        return count

    @property
    def indexes(self) -> List[int]:
        '''The list of indexes in the OD'''

        return list(self._data.keys())

    @property
    def mandatory_objects(self) -> List[int]:
        '''The list of mandatory objects indexes in the OD'''

        objects = []

        for i in self.MANDATORY_OBJECTS:
            if i in self._data:
                objects.append(i)

        return objects

    @property
    def optional_objects(self) -> list:
        '''The list of optional objects indexes in the OD'''

        objects = []

        for i in self._data:
            if (i >= 0x1000 and i <= 0x1FFF and i not in self.MANDATORY_OBJECTS) \
                    or (i >= 0x6000 and i <= 0xFFFF):
                objects.append(i)

        return objects

    @property
    def manufacturer_objects(self) -> List[int]:
        '''The list of manufacturer objects indexes in the OD'''

        objects = []

        for i in self._data:
            if i >= 0x2000 and i <= 0x5FFF:
                objects.append(i)

        return objects

    @property
    def storage_locations(self) -> List[str]:
        '''The list of storage locations for CANopenNode support.'''

        return self._storage_locations

    def add_storage_location(self, storage_location: str):

        if storage_location not in self._storage_locations and storage_location != '':
            self._storage_locations.append(storage_location)

    def copy_object(self, index: int, subindex: int, new_index: int, new_subindex: int,
                    move: bool = False):
        '''Move or copy an object in the OD'''

        if index not in self.indexes:
            raise EDSError(f'no object exists at index 0x{index:X}')
        if subindex is not None and subindex not in self._data[index].subindexes:
            raise EDSError(f'no object exists at index 0x{index:X} subindex 0x{subindex:02X}')

        if new_subindex is None and new_index in self._data:
            raise EDSError(f'object already exist at index 0x{new_index:X}')
        if new_subindex is not None:
            if isinstance(self._data[new_index], Variable):
                raise EDSError('cannot move an object to a subindex of an Variable')
            if new_subindex in self._data[new_index].subindexes:
                raise EDSError(f'object already exist at index 0x{new_index:X} subindex '
                               f'0x{new_subindex:02X}')

        if not isinstance(self._data[index], Variable) and new_subindex is not None:
            raise EDSError('cannot move a non-Variable to a subindex')

        obj = self._data[index] if subindex is None else self._data[index][subindex]

        if new_subindex is None:
            self._data[new_index] = deepcopy(obj)
        else:
            self._data[new_index][new_subindex] = deepcopy(obj)

        if move:
            if subindex is None:
                del self._data[index]
            else:
                del self._data[index][subindex]
