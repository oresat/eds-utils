import sys
import argparse

from .app import App

EDS_EDITOR_DESCRIPTION = 'A GUI to edit EDS/DCF files'


def eds_editor(sys_args=None):
    if sys_args is None:
        sys_args = sys.argv[1:]

    name = 'eds-editor'
    parser = argparse.ArgumentParser(description=EDS_EDITOR_DESCRIPTION, prog=name)
    parser.add_argument('filepath', nargs='*', default='', metavar='FILEPATH',
                        help='file path(s) to EDS file(s)')
    args = parser.parse_args(sys_args)

    app = App()
    if args.filepath:
        app.open_file(args.filepath[0])  # TODO handle multiple files
    app.run()
