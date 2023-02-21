from os import remove
from os.path import basename
from copy import deepcopy

from gi.repository import Gtk, GLib

from ..core.file_io.read_eds import read_eds
from ..core.file_io.write_eds import write_eds
from .dialogs.errors_dialog import ErrorsDialog
from .pages.general_info_page import GeneralInfoPage
from .pages.object_dictionary_page import ObjectDictionaryPage
from .pages.device_commissioning_page import DeviceCommissioningPage
from .pages.pdo_page import PDOPage


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

        self.eds_bak = deepcopy(self.eds)

        if errors:
            errors_dialog = ErrorsDialog(self.parent_window)
            errors_dialog.errors = errors
            errors_dialog.show()

        self.gi_page = GeneralInfoPage(self.eds)
        self.od_page = ObjectDictionaryPage(self.eds, self.parent_window)
        self.rpdo_page = PDOPage(self.eds, self.parent_window, 'RPDO')
        self.tpdo_page = PDOPage(self.eds, self.parent_window, 'TPDO')
        self.dc_page = DeviceCommissioningPage(self.eds)

        self.append_page(self.gi_page, Gtk.Label.new('General Info'))
        self.append_page(self.od_page, Gtk.Label.new('Object Dictionary'))
        self.append_page(self.rpdo_page, Gtk.Label.new('RPDOs'))
        self.append_page(self.tpdo_page, Gtk.Label.new('TPDOs'))
        self.append_page(self.dc_page, Gtk.Label.new('Device Commissioning'))

        self.connect('switch-page', self._on_page_changed)

        # save a tempory eds file at an interval
        GLib.timeout_add_seconds(30, self._save_eds_tmp)

    def _on_page_changed(self, notebook: Gtk.Notebook, page: Gtk.Widget, page_num: int):
        '''Refresh the new page'''

        page.refresh()

    def save_eds(self, file_path=''):
        '''Save the eds file'''

        if not file_path:
            file_path = self.file_path

        write_eds(self.eds, file_path)

        self.eds_bak = deepcopy(self.eds)

        # remove temp
        try:
            remove(self.tmp_file_path)
        except OSError:
            pass

    def _save_eds_tmp(self):
        '''Save a tempory eds file'''

        if self.eds != self.eds_bak:  # only save a temp if something has changed
            write_eds(self.eds, self.tmp_file_path)

            self.eds_bak = deepcopy(self.eds)

        return True

    @property
    def eds_file(self) -> str:
        '''str: The EDS file name.'''

        return basename(self.file_path)

    @property
    def eds_has_changed(self) -> bool:
        '''bool: Flag if the eds file has change and not been saved.'''

        ret = False
        if True in [self.gi_page.eds_has_changed, self.od_page.eds_has_changed,
                    self.rpdo_page.eds_has_changed, self.tpdo_page.eds_has_changed,
                    self.dc_page.eds_has_changed]:
            ret = True

        return ret
