import sys
import argparse

from .core.file_io.read_eds import read_eds
from .core.file_io.write_md import write_md
from .core.file_io.write_rst import write_rst

EDS_CONVERT_DESCRIPTION = 'Convert EDS/DCF to other formats CLI tool'

EPILOG = '''\
Supported output extensions:
  .md - markdown
  .rst - reStructuredText
'''


def eds_convert(sys_args=None):
    if sys_args is None:
        sys_args = sys.argv[1:]

    name = 'eds-convert'
    parser = argparse.ArgumentParser(description=EDS_CONVERT_DESCRIPTION, prog=name,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=EPILOG)
    parser.add_argument('input', metavar='INPUT', help='filepath to EDS/DCF file')
    parser.add_argument('output', metavar='OUTPUT', help='output file path')
    args = parser.parse_args(sys_args)

    try:
        eds, errors = read_eds(args.input)
    except FileNotFoundError as exc:
        print(exc)
        sys.exit(1)

    dcf = False
    if args.input.endswith('.dcf'):
        dcf = True

    if args.output.endswith('.md'):
        write_md(eds, file_path=args.output, dcf=dcf)
    elif args.output.endswith('.rst'):
        write_rst(eds, file_path=args.output, dcf=dcf)
    else:
        print('Unknown output extension')
        print('')
        print(EPILOG)
