from os import remove
from os.path import basename

from gi.repository import Gtk, GLib

from ..core.file_io.read_eds import read_eds
from ..core.file_io.write_eds import write_eds
from .dialogs.errors_dialog import ErrorsDialog
from .pages.general_info_page import GeneralInfoPage
from .pages.object_dictionary_page import ObjectDictionaryPage
from .pages.device_commissioning_page import DeviceCommissioningPage


class EDSNotebook(Gtk.Notebook):

    def __init__(self, file_path: str, parent_window: Gtk.Window):
        '''
        Parameters
        ----------
        file_path: str
            THe path to the eds/dcf file to edit.
        parent_window: Gtk.Window
            The parent window to open dialogs with (dialogs require references to the parent
            window).
        '''
        super().__init__()

        # need the parent window for dialogs
        self.parent_window = parent_window

        self.file_path = file_path
        self.tmp_file_path = file_path + '.tmp'
        self.eds, errors = read_eds(self.file_path)

        if errors:
            errors_dialog = ErrorsDialog(self.parent_window)
            errors_dialog.errors = errors
            errors_dialog.show()

        self.gi_page = GeneralInfoPage(self.eds)
        self.od_page = ObjectDictionaryPage(self.eds, self.parent_window)
        self.dc_page = DeviceCommissioningPage(self.eds)

        self.append_page(self.gi_page, Gtk.Label.new('General Info'))
        self.append_page(self.od_page, Gtk.Label.new('Object Dictionary'))
        self.append_page(self.dc_page, Gtk.Label.new('Device Commissioning'))

        # save a tempory eds file at an interval
        GLib.timeout_add_seconds(30, self._save_eds_tmp)

    def _eds_changed_reset(self):
        '''Reset the eds changed flags'''

        self.gi_page.eds_changed_reset()
        self.od_page.eds_changed_reset()
        self.dc_page.eds_changed_reset()

    def save_eds(self, file_path=''):
        '''Save the eds file'''

        if file_path:
            file_path = self.file_path

        write_eds(self.eds, file_path)

        self._eds_changed_reset()

        # remove temp
        try:
            remove(self.tmp_file_path)
        except OSError:
            pass

    def _save_eds_tmp(self):
        '''Save a tempory eds file'''

        if self.eds_changed:  # only save a temp if something has changed
            write_eds(self.eds, self.tmp_file_path)

            self._eds_changed_reset()

        return True

    @property
    def eds_file(self) -> str:
        '''str: The EDS file name.'''

        return basename(self.file_path)

    @property
    def eds_changed(self) -> bool:
        '''bool: Flag if the eds file has change and not been saved.'''

        ret = False
        if self.gi_page.eds_changed or self.od_page.eds_changed or self.dc_page.eds_changed:
            ret = True

        return ret
