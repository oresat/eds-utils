from gi.repository import Gtk

from ...core.eds import EDS


class Page(Gtk.ScrolledWindow):

    def __init__(self):
        super().__init__()

        self._eds = None
        self._eds_changed = False

    def load_eds(self, eds: EDS):
        self._eds = eds

    def remove_eds(self):
        self._eds = None

    @property
    def eds_changed(self) -> bool:
        return self._eds_changed

    def eds_changed_reset(self):
        self._eds_changed = False
