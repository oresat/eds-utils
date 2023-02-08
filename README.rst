=========
eds-utils
=========

A collection of EDS / DCF utilities.

Utilities
=========

- **eds-editor:** GTK4-based GUI to edit EDS / DCF files.
- **eds-validate:** CLI to validate EDS / DCF files. Will print all errors to stderr.
- **eds2c:** CLI to convert a EDS / DCF file to CANopenNode OD.[c/h] files.
- **eds2dcf:** CLI to convert a EDS to a DCF.
- **eds2md:** CLI to convert a EDS / DCF file to a md (Markdown) file.
- **eds2rst:** CLI to convert a EDS / DCF file to a rst (reStructuredText) file.
- **eds-autofix:** CLI to autofix errors in EDS / DCF files.


How To Install
==============

Linux
-----

- Install GTK4 for your distro

  - For Arch based distros:``$ sudo pacman -S gtk4 python-gobject``
  - For Debian based distros:``$ sudo apt install gtk4 python3-gi``

- Install eds-utils with pip: ``$ pip install eds-utils``

MacOS
-----

- Install GTK4 for your system

  - With Homebrew:``$ brew install gtk4 pyobject3``
  - With MacPorts:``$ sudo ports install gtk4 py-object3``

- Install eds-utils with pip: ``$ pip3 install eds-utils``
