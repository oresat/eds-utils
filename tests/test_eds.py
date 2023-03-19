import unittest

from eds_utils.core.objects import Variable, Record
from eds_utils.core.eds import EDS, EDSError


class TestEDS(unittest.TestCase):

    def test_insert(self):
        eds = EDS()

        # add a var to eds
        eds.insert(0x8000, None, Variable())
        self.assertEqual(len(eds.indexes), 1)

        # index already exist
        with self.assertRaises(EDSError):
            eds.insert(0x8000, None, Variable())
        self.assertEqual(len(eds.indexes), 1)

        # cannont insert an var as subindex to another var
        with self.assertRaises(EDSError):
            eds.insert(0x8000, 1, Variable())
        self.assertEqual(len(eds.indexes), 1)

        # add a rec to eds
        eds.insert(0x8100, None, Record())
        self.assertEqual(len(eds.indexes), 2)

        # add var to rec
        eds.insert(0x8100, 1, Variable())
        self.assertEqual(len(eds.indexes), 2)

        # try to re-insert var again
        with self.assertRaises(EDSError):
            eds.insert(0x8100, 1, Variable())
        self.assertEqual(len(eds.indexes), 2)

    def test_remove(self):
        eds = EDS()

        # try to remove something that doesn't exist
        with self.assertRaises(KeyError):
            eds.remove(0x8000, None)

        # try to remove something that doesn't exist
        with self.assertRaises(KeyError):
            eds.remove(0x8000, 1)

        # remove objects from eds
        for i in range(0x5000, 0x5010):
            eds.insert(i, None, Record())
        self.assertEqual(len(eds.indexes), 0x10)
        for i in range(0x5000, 0x5010):
            eds.remove(i)
        self.assertEqual(len(eds.indexes), 0)

        # remove a record from eds
        eds.insert(0x5000, None, Record())
        for i in range(1, 10):
            eds.insert(0x5000, i, Variable())
        self.assertEqual(len(eds.indexes), 1)
        self.assertEqual(len(eds[0x5000].subindexes), 10)
        eds.remove(0x5000)
        self.assertEqual(len(eds.indexes), 0)

        # remove objects from eds
        eds.insert(0x5000, None, Record())
        for i in range(1, 10):
            eds.insert(0x5000, i, Variable())
        self.assertEqual(len(eds.indexes), 1)
        self.assertEqual(len(eds[0x5000].subindexes), 10)
        for i in range(1, 10):
            eds.remove(0x5000, i)
        self.assertEqual(len(eds[0x5000].subindexes), 1)
        eds.remove(0x5000)
        self.assertEqual(len(eds.indexes), 0)

    def test_rpdo(self):
        eds = EDS()

        eds.add_rpdo()
        self.assertEqual(len(eds.indexes), 2)
        eds[0x1400]
        eds[0x1600]
        self.assertEqual(eds.rpdos, 1)

        eds.add_rpdo()
        self.assertEqual(len(eds.indexes), 4)
        eds[0x1401]
        eds[0x1601]
        self.assertEqual(eds.rpdos, 2)

    def test_tpdo(self):
        eds = EDS()

        eds.add_tpdo()
        self.assertEqual(len(eds.indexes), 2)
        eds[0x1800]
        eds[0x1A00]
        self.assertEqual(eds.tpdos, 1)

        eds.add_tpdo()
        self.assertEqual(len(eds.indexes), 4)
        eds[0x1801]
        eds[0x1A01]
        self.assertEqual(eds.tpdos, 2)
