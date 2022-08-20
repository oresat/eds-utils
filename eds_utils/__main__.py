import sys

from . import __version__
from .eds_validate import eds_validate, EDS_VALIDATE_DESCRIPTION
from .eds_editor.main import eds_editor, EDS_EDITOR_DESCRIPTION
from .eds2dcf import eds2dcf, EDS2DCF_DESCRIPTION
from .eds_convert import eds_convert, EDS_CONVERT_DESCRIPTION


PROGRAMS = {
    'eds-validate': EDS_VALIDATE_DESCRIPTION,
    'eds2dcf': EDS2DCF_DESCRIPTION,
    'eds-editor': EDS_EDITOR_DESCRIPTION,
    'eds-convert': EDS_CONVERT_DESCRIPTION,
}


def eds_utils():
    print('')
    print('eds-utils v' + __version__)
    print('')

    print('command : description')
    print('---------------------')
    for i in PROGRAMS:
        print(i + ' : ' + PROGRAMS[i])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        eds_utils()
    elif sys.argv[1] == 'eds-validate':
        eds_validate(sys.argv[2:])
    elif sys.argv[1] == 'eds2dcf':
        eds2dcf(sys.argv[2:])
    elif sys.argv[1] == 'eds-editor':
        eds_editor(sys.argv[2:])
    elif sys.argv[1] == 'eds-convert':
        eds_convert(sys.argv[2:])
    else:
        eds_utils()
