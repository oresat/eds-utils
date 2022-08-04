import sys
import argparse

from .core.file_io.read_eds import read_eds

VALIDATE_EDS_DESCRIPTION = 'Validate EDS/DCF file'


def validate_eds(sys_args=None):
    if sys_args is None:
        sys_args = sys.argv[1:]

    name = 'validate-eds'
    parser = argparse.ArgumentParser(description=VALIDATE_EDS_DESCRIPTION, prog=name)
    parser.add_argument('filepath', metavar='FILEPATH', help='filepath to EDS file')
    parser.add_argument('-s', '--silence', action='store_true', help='silence prints to stderr')
    args = parser.parse_args(sys_args)

    _, errors = read_eds(args.filepath)

    if not args.silence:
        for i in errors:
            print(i, file=sys.stderr)

    if len(errors) > 0:
        sys.exit(1)
