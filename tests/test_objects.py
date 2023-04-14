import unittest

from eds_utils.core import DataType
from eds_utils.core.objects import Variable, Record, Array


class TestRecord(unittest.TestCase):

    def test_add(self):

        rec = Record()

        # check default values
        self.assertEqual(len(rec), 1)
        self.assertEqual(rec[0].default_value, '0x00')

        # add a var to an subindex
        rec[1] = Variable()
        self.assertEqual(len(rec), 2)
        self.assertEqual(rec[0].default_value, '0x01')

        # try to var in subindex that exist
        with self.assertRaises(ValueError):
            rec[1] = Variable()
        self.assertEqual(len(rec), 2)
        self.assertEqual(rec[0].default_value, '0x01')

        # add second subindex
        rec[2] = Variable()
        self.assertEqual(len(rec), 3)
        self.assertEqual(rec[0].default_value, '0x02')

        # empty space
        rec[4] = Variable()
        self.assertEqual(len(rec), 4)
        self.assertEqual(rec[0].default_value, '0x04')

    def test_remove(self):

        rec = Record()

        # add a var to an subindex
        rec[1] = Variable()
        rec[2] = Variable()
        rec[3] = Variable()
        rec[5] = Variable()

        # cannot remove subindex 0
        with self.assertRaises(ValueError):
            del rec[0]

        # cannot remove an index that doesn't exist
        with self.assertRaises(ValueError):
            del rec[4]

        # remove a valid subindexes
        self.assertEqual(len(rec), 5)
        self.assertEqual(rec[0].default_value, '0x05')
        del rec[3]
        self.assertEqual(len(rec), 4)
        self.assertEqual(rec[0].default_value, '0x03')
        del rec[1]
        self.assertEqual(len(rec), 3)
        self.assertEqual(rec[0].default_value, '0x02')
        del rec[5]
        self.assertEqual(len(rec), 2)
        self.assertEqual(rec[0].default_value, '0x01')
        del rec[2]
        self.assertEqual(len(rec), 1)
        self.assertEqual(rec[0].default_value, '0x00')

        # cannot remove subindex 0
        with self.assertRaises(ValueError):
            del rec[0]


class TestArray(unittest.TestCase):

    def test_add(self):

        arr = Array(data_type=DataType.UNSIGNED8)

        # add a var to an subindex
        arr[1] = Variable(data_type=DataType.UNSIGNED8)
        self.assertEqual(len(arr), 2)
        self.assertEqual(arr[0].default_value, '0x01')

        # try add a var not matching array data type
        with self.assertRaises(ValueError):
            arr[1] = Variable(data_type=DataType.UNSIGNED16)
        self.assertEqual(len(arr), 2)
        self.assertEqual(arr[0].default_value, '0x01')

        # add a var to an subindex
        arr[10] = Variable(data_type=DataType.UNSIGNED8)
        self.assertEqual(len(arr), 3)
        self.assertEqual(arr[0].default_value, '0x0A')

        for i in arr.subindexes:
            self.assertEqual(arr[i].data_type, arr.data_type)

    def test_data_type(self):

        arr = Array(data_type=DataType.UNSIGNED32)
        for i in range(1, 10):
            arr[i] = Variable(data_type=DataType.UNSIGNED32)

        # make sure all subindex data types are the same as arrays
        for i in arr.subindexes:
            if i == 0:  # subindex 0 must be a UNSIGNED8
                self.assertEqual(arr[i].data_type, DataType.UNSIGNED8)
            else:
                self.assertEqual(arr[i].data_type, arr.data_type)

        # update data type for array
        arr.data_type = DataType.UNSIGNED16
        self.assertEqual(arr.data_type, DataType.UNSIGNED16)

        # all subindex should be updated
        for i in arr.subindexes:
            if i == 0:  # subindex 0 must stay UNSIGNED8
                self.assertEqual(arr[i].data_type, DataType.UNSIGNED8)
            else:
                self.assertEqual(arr[i].data_type, arr.data_type)
