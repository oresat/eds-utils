import os
import sys
import argparse

from .core.file_io.read_eds import read_eds
from .core.file_io.write_md import write_md

EDS2MD_DESCRIPTION = 'Convert a EDS/DCF file to a md (Markdown) file'


def eds2md(sys_args=None):
    if sys_args is None:
        sys_args = sys.argv[1:]

    parser = argparse.ArgumentParser(description=EDS2MD_DESCRIPTION, prog='eds2md')
    parser.add_argument('filepath', metavar='FILEPATH', help='file path to EDS file')
    parser.add_argument('-o', '--output', metavar='OUTPUT', help='output file path')
    args = parser.parse_args(sys_args)

    try:
        eds, errors = read_eds(args.filepath)
    except FileNotFoundError as exc:
        print(exc)
        sys.exit(1)

    if args.output:
        write_md(eds, file_path=args.output)
    else:
        path = os.path.dirname(os.path.abspath(args.filepath))
        file_name = os.path.basename(args.filepath)[:-4] + '.md'
        write_md(eds, file_path=f'{path}/{file_name}')
