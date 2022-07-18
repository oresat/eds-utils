from os.path import basename

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

        self.notebook = Gtk.Notebook()
        self.set_child(self.notebook)

        self.gi_page = GeneralInfoPage()
        self.od_page = ObjectDictionaryPage()
        self.dc_page = DeviceCommissioningPage()

        self.notebook.append_page(self.gi_page, Gtk.Label.new('General Info'))
        self.notebook.append_page(self.od_page, Gtk.Label.new('Object Dictionary'))
        self.notebook.append_page(self.dc_page, Gtk.Label.new('Device Commissioning'))

        self.header = Gtk.HeaderBar()
        self.set_titlebar(self.header)

        f = Gtk.FileFilter()
        f.set_name('CANopen files')
        f.add_pattern('*.dcf')
        f.add_pattern('*.eds')

        button = Gtk.Button(label='Open')
        button.set_icon_name('document-open-symbolic')
        button.set_tooltip_text('Open a project')
        button.connect('clicked', self.show_open_dialog)
        self.open_dialog = Gtk.FileChooserNative.new(title='Choose a file', parent=self,
                                                     action=Gtk.FileChooserAction.OPEN)
        self.open_dialog.connect('response', self.open_response)
        self.open_dialog.add_filter(f)
        self.header.pack_start(button)

        button = Gtk.Button(label='New')
        button.set_icon_name('document-new-symbolic')
        button.set_tooltip_text('Create a new project')
        button.connect('clicked', self.show_new_dialog)
        self.header.pack_start(button)

        button = Gtk.Button(label='Close')
        button.set_icon_name('edit-clear-symbolic')
        button.set_tooltip_text('Close the project')
        button.connect('clicked', self.on_click_close)
        self.header.pack_end(button)

        button = Gtk.Button(label='Save As')
        button.set_icon_name('document-save-as-symbolic')
        button.set_tooltip_text('Save the current project as a different name')
        button.connect('clicked', self.show_save_as_dialog)
        self.save_as_dialog = Gtk.FileChooserNative.new(title='Choose a file', parent=self,
                                                        action=Gtk.FileChooserAction.SAVE)
        self.save_as_dialog.connect('response', self.save_as_response)
        self.save_as_dialog.add_filter(f)
        self.header.pack_end(button)

        button = Gtk.Button(label='Save')
        button.set_icon_name('document-save-symbolic')
        button.set_tooltip_text('Save the project')
        button.connect('clicked', self.on_click_save)
        self.header.pack_end(button)

    def open_file(self, file_path):
        self.file_path = file_path
        self.header.set_title_widget(Gtk.Label.new(basename(file_path)))
        self.eds = EDS()
        self.eds.load(file_path)

        self.gi_page.load_eds(self.eds)
        self.od_page.load_eds(self.eds)
        self.dc_page.load_eds(self.eds)

    def save_file(self, file_path: str = None):
        self.eds.save(file_path)

    def show_new_dialog(self, button):
        print('new TODO')

    def show_open_dialog(self, button):
        self.open_dialog.show()

    def open_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            file_path = file.get_path()
            self.open_file(file_path)

    def on_click_save(self, button):
        if self.file_path:
            self.save_file(self.file_path)

    def show_save_as_dialog(self, button):
        self.save_as_dialog.show()

    def save_as_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            file_path = file.get_path()
            self.save_file(file_path)

    def on_click_close(self, button):
        print('close TODO')
