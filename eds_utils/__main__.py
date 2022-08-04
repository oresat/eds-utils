import sys

from . import __version__
from .validate_eds import validate_eds, VALIDATE_EDS_DESCRIPTION
from .eds_editor.main import eds_editor, EDS_EDITOR_DESCRIPTION
from .eds2dcf import eds2dcf, EDS2DCF_DESCRIPTION


PROGRAMS = {
    'validate-eds': VALIDATE_EDS_DESCRIPTION,
    'eds2dcf': EDS2DCF_DESCRIPTION,
    'eds-editor': EDS_EDITOR_DESCRIPTION,
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
    elif sys.argv[1] == 'validate-eds':
        validate_eds(sys.argv[2:])
    elif sys.argv[1] == 'eds2dcf':
        eds2dcf(sys.argv[2:])
    elif sys.argv[1] == 'eds-editor':
        eds_editor(sys.argv[2:])
    else:
        eds_utils()