from enum import Enum, auto


from gi.repository import Gtk


class TmpResponse(Enum):
    '''All Response to ObjectDictionaryPage'''

    USE_TMP = auto()
    DONT_USE_TMP = auto()
    DELETE_TMP = auto()


class OpenTmpDialog(Gtk.Dialog):
    '''Gtk Dialog to see if the user want to use the tempory from the eds-editor or actual eds
    file.'''

    def __init__(self, parent: Gtk.Window, file_path: str):
        '''
        Parameter
        ---------
        parent: Gtk.Window
            The parent window to attach to.
        file_path: str
            The file path to eds file.
        '''

        super().__init__(title='Open Tmp', transient_for=parent)

        self._file_path = file_path
        self._use_tmp = 0

        self.set_default_size(500, 500)

        box = self.get_content_area()

        grid = Gtk.Grid(column_spacing=5, row_spacing=5, margin_top=5, margin_bottom=5,
                        margin_start=5, margin_end=5)
        box.append(grid)

        label = Gtk.Label.new('EDS Editor has found a tempory')
        grid.attach(label, column=0, row=0, width=2, height=1)

        button = Gtk.Button(label='Use Temp')
        button.set_halign(Gtk.Align.END)
        button.set_valign(Gtk.Align.END)
        button.connect('clicked', self.on_use_button_clicked)
        grid.attach(button, column=0, row=1, width=1, height=1)

        button = Gtk.Button(label='Don\'t use temp')
        button.set_halign(Gtk.Align.CENTER)
        button.set_valign(Gtk.Align.END)
        button.connect('clicked', self.on_dont_use_button_clicked)
        grid.attach(button, column=1, row=1, width=1, height=1)

        button = Gtk.Button(label='Don\'t use temp and delete it')
        button.set_halign(Gtk.Align.START)
        button.set_valign(Gtk.Align.END)
        button.connect('clicked', self.on_delete_tmp_button_clicked)
        grid.attach(button, column=2, row=1, width=1, height=1)

    def on_use_button_clicked(self, button: Gtk.Button):
        '''On the use the tmp file button clicked, close the dialog'''

        self._use_tmp = TmpResponse.USE_TMP
        self.response(1)
        self.destroy()

    def on_dont_use_button_clicked(self, button: Gtk.Button):
        '''On the don't use tmp button clicked, close the dialog.'''

        self._use_tmp = TmpResponse.DONT_USE_TMP
        self.response(1)
        self.destroy()

    def on_delete_tmp_button_clicked(self, button: Gtk.Button):
        '''On the don't use tmp and delte it button clicked, close the dialog.'''

        self._use_tmp = TmpResponse.DELETE_TMP
        self.response(1)
        self.destroy()

    def get_response(self) -> bool:
        '''
        Get the custom response from the dialog.

        Returns
        -------
        bool
            If the tmp should be used or not.
        '''

        return self._use_tmp

    @property
    def file_path(self) -> str:
        '''list: The file path of request eds file.'''

        return self._file_path
