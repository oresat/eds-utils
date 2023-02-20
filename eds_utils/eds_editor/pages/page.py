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

    def refresh(self):
        '''Refresh the page'''

        pass
