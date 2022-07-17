from gi.repository import Gtk

from .general_info_page import GeneralInfoPage
from .object_dictionary_page import ObjectDictionaryPage
from .device_commissioning_page import DeviceCommissioningPage
from ..core.eds import EDS


class AppWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.eds = None
        self.file_path = None

        # Create Notebook
        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        self.gi_page = GeneralInfoPage()
        self.od_page = ObjectDictionaryPage()
        self.dc_page = DeviceCommissioningPage()

        self.notebook.append_page(self.gi_page.page, Gtk.Label.new('General Info'))
        self.notebook.append_page(self.od_page.page, Gtk.Label.new('Object Dictionary'))
        self.notebook.append_page(self.dc_page.page, Gtk.Label.new('Device Commissioning'))

    def open_file(self, file_path):
        self.file_path = file_path
        self.eds = EDS()
        self.eds.load(file_path)

        self.gi_page.load_eds(self.eds)
        self.od_page.load_eds(self.eds)
        self.dc_page.load_eds(self.eds)

    def save(self, file_path: str = None):
        self.eds.save(file_path)
