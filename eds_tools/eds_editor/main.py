import sys
import argparse

from .app import App

EDS_EDITOR_DESCRIPTION = 'GUI to edit EDS files.'


def eds_editor(sys_args=None):
    if sys_args is None:
        sys_args = sys.argv[1:]

    name = 'eds-editor'
    parser = argparse.ArgumentParser(description=EDS_EDITOR_DESCRIPTION, prog=name)
    parser.add_argument('filepath', metavar='FILEPATH', help='filepath to EDS file')
    args = parser.parse_args(sys_args)

    app = App()
    app.open_file(args.filepath)
    app.run()
