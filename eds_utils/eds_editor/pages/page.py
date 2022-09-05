from gi.repository import Gtk

from ...core.eds import EDS


class Page(Gtk.ScrolledWindow):

    def __init__(self):
        super().__init__()

        self._eds = None

    def load_eds(self, eds: EDS):
        self._eds = eds

    def remove_eds(self):
        self._eds = None
