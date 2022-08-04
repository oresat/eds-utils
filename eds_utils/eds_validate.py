import sys
import argparse

from .core.file_io.read_eds import read_eds

EDS_VALIDATE_DESCRIPTION = 'Validate EDS/DCF files'


def eds_validate(sys_args=None):
    if sys_args is None:
        sys_args = sys.argv[1:]

    name = 'eds-validate'
    parser = argparse.ArgumentParser(description=EDS_VALIDATE_DESCRIPTION, prog=name)
    parser.add_argument('filepath', metavar='FILEPATH', help='filepath to EDS/DCF file')
    parser.add_argument('-s', '--silence', action='store_true', help='silence prints to stderr')
    args = parser.parse_args(sys_args)

    _, errors = read_eds(args.filepath)

    if not args.silence:
        for i in errors:
            print(i, file=sys.stderr)

    if len(errors) > 0:
        sys.exit(1)