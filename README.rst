eds-utils
=========

A collection of EDS / DCF utilities.

Utilities
---------

- **eds-editor:** GTK4-based GUI to edit eds/dcf files
- **eds-validate:** quick eds/dcf validator
- **eds2dcf:** quick eds to dcf converter
- **eds2md:** quick eds/dcf to md converter
- **eds2rst:** quick eds/dcf to rst converter


How To Run (From Repo)
----------------------

- Install Python and GTK4 for your system
- Install python libraries: ``$ pip install -r requirements.txt``
- To run the eds-editor (requires GTK4): ``$ python -m eds_utils eds-editor``
- To run the eds-validate: ``$ python -m eds_utils eds-validate EDS_FILE``
- To run the eds2dcf: ``$ python -m eds_utils eds2dcf EDS_FILE``
- To run the eds2md: ``$ python -m eds_utils eds2md EDS_FILE``
- To run the eds2rst: ``$ python -m eds_utils eds2rst EDS_FILE``
