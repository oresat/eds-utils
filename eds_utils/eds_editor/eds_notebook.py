from os.path import basename

from gi.repository import Gtk

from ..core.file_io.read_eds import read_eds
from ..core.file_io.write_eds import write_eds
from .dialogs.errors_dialog import ErrorsDialog
from .pages.general_info_page import GeneralInfoPage
from .pages.object_dictionary_page import ObjectDictionaryPage
from .pages.device_commissioning_page import DeviceCommissioningPage


class EDSNotebook(Gtk.Notebook):
    def __init__(self, file_path: str, parent_window: Gtk.Window):
        super().__init__()

        # need the parent window for dialogs
        self.parent_window = parent_window

        self.file_path = file_path
        self.eds, errors = read_eds(self.file_path)

        if errors:
            errors_dialog = ErrorsDialog(self.parent_window)
            errors_dialog.errors = errors
            errors_dialog.show()

        self.gi_page = GeneralInfoPage()
        self.od_page = ObjectDictionaryPage(self.parent_window)
        self.dc_page = DeviceCommissioningPage()

        self.append_page(self.gi_page, Gtk.Label.new('General Info'))
        self.append_page(self.od_page, Gtk.Label.new('Object Dictionary'))
        self.append_page(self.dc_page, Gtk.Label.new('Device Commissioning'))

        self.gi_page.load_eds(self.eds)
        self.od_page.load_eds(self.eds)
        self.dc_page.load_eds(self.eds)

    def save_eds(self, file_path=''):

        if file_path:
            file_path = self.file_path

        write_eds(self.eds, file_path)

    @property
    def eds_file(self) -> str:
        return basename(self.file_path)
