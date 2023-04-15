import sys
import argparse

from .core.file_io.read_eds import read_eds
from .core.file_io.write_eds import write_eds

EDS_AUTOFIX_DESCRIPTION = 'Autofix errors in a EDS/DCF file'


def eds_autofix(sys_args=None):
    if sys_args is None:
        sys_args = sys.argv[1:]

    parser = argparse.ArgumentParser(description=EDS_AUTOFIX_DESCRIPTION, prog='eds-autofix')
    parser.add_argument('filepath', metavar='FILEPATH', help='file path to EDS/DCF file')
    parser.add_argument('-s', '--silence', action='store_true', help='silence prints to stdout')
    args = parser.parse_args(sys_args)

    try:
        eds, errors = read_eds(args.filepath)
        write_eds(eds, args.filepath)
    except FileNotFoundError as exc:
        print(exc)
        sys.exit(1)

    if not args.silence:
        for i in errors:
            print(i)
