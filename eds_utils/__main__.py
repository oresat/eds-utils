import sys

from . import __version__
from .eds_validate import eds_validate, EDS_VALIDATE_DESCRIPTION
from .eds_editor.main import eds_editor, EDS_EDITOR_DESCRIPTION
from .eds2dcf import eds2dcf, EDS2DCF_DESCRIPTION
from .eds2md import eds2md, EDS2MD_DESCRIPTION
from .eds2rst import eds2rst, EDS2RST_DESCRIPTION
from .eds2c import eds2c, EDS2C_DESCRIPTION
from .eds_autofix import eds_autofix, EDS_AUTOFIX_DESCRIPTION
from .eds_merge import eds_merge, EDS_MERGE_DESCRIPTION


PROGRAMS = {
    'eds-validate': EDS_VALIDATE_DESCRIPTION,
    'eds-editor  ': EDS_EDITOR_DESCRIPTION,
    'eds2dcf     ': EDS2DCF_DESCRIPTION,
    'eds2md      ': EDS2MD_DESCRIPTION,
    'eds2rst     ': EDS2RST_DESCRIPTION,
    'eds2c       ': EDS2C_DESCRIPTION,
    'eds-autofix ': EDS_AUTOFIX_DESCRIPTION,
    'eds-merge   ': EDS_MERGE_DESCRIPTION,
}


def eds_utils():
    print('eds-utils v' + __version__)
    print('')

    print('command      : description')
    print('--------------------------')
    for i in PROGRAMS:
        print(i + ' : ' + PROGRAMS[i])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        eds_utils()
    elif sys.argv[1] == 'eds-validate':
        eds_validate(sys.argv[2:])
    elif sys.argv[1] == 'eds-editor':
        eds_editor(sys.argv[2:])
    elif sys.argv[1] == 'eds2dcf':
        eds2dcf(sys.argv[2:])
    elif sys.argv[1] == 'eds2md':
        eds2md(sys.argv[2:])
    elif sys.argv[1] == 'eds2rst':
        eds2rst(sys.argv[2:])
    elif sys.argv[1] == 'eds2c':
        eds2c(sys.argv[2:])
    elif sys.argv[1] == 'eds-autofix':
        eds_autofix(sys.argv[2:])
    elif sys.argv[1] == 'eds-merge':
        eds_merge(sys.argv[2:])
    else:
        eds_utils()
