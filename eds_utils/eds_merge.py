import sys
import argparse

from .core import ObjectType
from .core.file_io.read_eds import read_eds
from .core.file_io.write_eds import write_eds

EDS_MERGE_DESCRIPTION = 'Merge a EDS/DCF into another EDS/DCF'


def eds_merge(sys_args=None):
    if sys_args is None:
        sys_args = sys.argv[1:]

    parser = argparse.ArgumentParser(description=EDS_MERGE_DESCRIPTION, prog='eds-merge')
    parser.add_argument('filepath1', metavar='FILEPATH1',
                        help='file path to EDS/DCF file to merge from')
    parser.add_argument('filepath2', metavar='FILEPATH2',
                        help='file path to EDS/DCF file to merge into')
    parser.add_argument('-s', '--strategy', default='diff',
                        help='merge strategy (e.g. diff [default], override)')
    parser.add_argument('-t', '--tpdo', action='store_false', help='don\'t skip TPDOs')
    parser.add_argument('-r', '--rpdo', action='store_false', help='don\'t skip RPDOs')
    args = parser.parse_args(sys_args)

    strategy = args.strategy.lower()

    try:
        eds1, errors1 = read_eds(args.filepath1)
        eds2, errors2 = read_eds(args.filepath2)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)

    for index in eds1.indexes:
        if (args.rpdo and index >= eds1.RPDO_COMM_START and index <= eds1.RPDO_COMM_END) or \
                (args.tpdo and index >= eds1.TPDO_COMM_START and index <= eds1.TPDO_COMM_END):
            continue

        index_obj = eds1[index]

        if strategy == 'override' and index in eds2.indexes:
            del eds2[index]
        if index not in eds2.indexes:
            print(f'0x{index:04X}')
            eds2[index] = eds1[index]
        if strategy == 'override':
            continue  # no need to subindex after doing the full index

        if index_obj.object_type != ObjectType.VAR:
            for subindex in index_obj.subindexes:
                if subindex == 0:
                    continue
                if subindex not in eds2[index].subindexes:
                    print(f'0x{index:04X} sub 0x{subindex:02X}')
                    eds2[index][subindex] = eds1[index][subindex]

    # when merging an EDS into a DCF, update the LastEDS field
    if args.filepath1.endswith('.eds') and args.filepath2.endswith('.dcf'):
        eds2.file_info.last_eds = eds1.file_info.file_name

    write_eds(eds2)
