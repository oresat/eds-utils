from gi.repository import Gtk

from ...core.eds import EDS


class Page(Gtk.ScrolledWindow):
    '''Base class for an page in the eds editor.'''

    def __init__(self, eds: EDS):
        '''
        Parameter
        ---------
        eds: EDS
            The eds file for the page to use.
        '''
        super().__init__()

        self._eds = eds
        self._eds_changed = False

    @property
    def eds_changed(self) -> bool:
        '''bool: a flag to see if eds info has changed.'''
        return self._eds_changed

    def eds_changed_reset(self):
        '''Reset the eds changed flag.'''

        self._eds_changed = False
