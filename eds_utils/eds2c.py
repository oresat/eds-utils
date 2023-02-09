import os
import sys
import argparse

from .core.file_io.read_eds import read_eds
from .core.file_io.write_canopennode import write_canopennode

EDS2C_DESCRIPTION = 'Convert a EDS/DCF file to CANopenNode OD.[c/h] files'


def eds2c(sys_args=None):
    if sys_args is None:
        sys_args = sys.argv[1:]

    parser = argparse.ArgumentParser(description=EDS2C_DESCRIPTION, prog='eds2c')
    parser.add_argument('filepath', metavar='FILEPATH', help='file path to EDS file')
    parser.add_argument('-o', '--output', metavar='OUTPUT', help='output file path')
    args = parser.parse_args(sys_args)

    try:
        eds, errors = read_eds(args.filepath)
    except FileNotFoundError as exc:
        print(exc)
        sys.exit(1)

    if args.output:
        write_canopennode(eds, dir_path=args.output)
    else:
        write_canopennode(eds, dir_path=os.path.dirname(os.path.abspath(args.filepath)))
