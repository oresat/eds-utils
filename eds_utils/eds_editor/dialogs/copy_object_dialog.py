from gi.repository import Gtk

from ...core import ObjectType, str2int
from ...core.eds import EDS


class CopyObjectDialog(Gtk.Dialog):
    '''Gtk Dialog to move or copy an object to a different index / subindex in the object
    dictionary.'''

    def __init__(self, parent: Gtk.Window, eds: EDS, index: int, subindex: int = None, move=False):
        '''
        Parameter
        ---------
        parent: Gtk.Window
            The parent window to attach to.
        eds: EDS
            The eds object to check if new object already exist. Dialog does not add new object.
        index: int
            The index of object to move/copy.
        subindex: int
            Optional: The subindex of object to move/copy.
        move: bool
            If True move the object to new index and subindex, if False copy the object to the new
            index and subindex.
        '''

        if move:
            title = 'Move object to new index/subindex'
        else:
            title = 'Copy object to new index/subindex'

        super().__init__(title=title, transient_for=parent)

        self.eds = eds
        self.index = index
        self.subindex = subindex
        self.move = move

        self._new_index = None
        self._new_subindex = None

        box = self.get_content_area()

        grid = Gtk.Grid(column_spacing=5, row_spacing=5, margin_top=5, margin_bottom=5,
                        margin_start=5, margin_end=5)
        box.append(grid)

        if move:
            label = Gtk.Label(label='Object to move:')
        else:
            label = Gtk.Label(label='Object to copy:')
        label.set_halign(Gtk.Align.START)
        grid.attach(label, column=0, row=0, width=1, height=1)

        if subindex is None:
            name = self.eds[index].parameter_name
            label = Gtk.Label(label=f'{name} at 0x{index:X}')
        else:
            name = self.eds[index][subindex].parameter_name
            label = Gtk.Label(label=f'{name} at 0x{index:X} sub 0x{subindex:X}')
        grid.attach(label, column=1, row=0, width=1, height=1)

        label = Gtk.Label(label='New Index:')
        label.set_halign(Gtk.Align.START)
        self.index_entry = Gtk.Entry()
        self.index_entry.set_text(f'0x{self.index:04X}')
        grid.attach(label, column=0, row=1, width=1, height=1)
        grid.attach(self.index_entry, column=1, row=1, width=1, height=1)

        label = Gtk.Label(label='New Subindex (optional):')
        label.set_halign(Gtk.Align.START)
        self.subindex_entry = Gtk.Entry()
        if self.subindex is not None:
            self.subindex_entry.set_text(f'0x{self.subindex:02X}')
        grid.attach(label, column=2, row=1, width=1, height=1)
        grid.attach(self.subindex_entry, column=3, row=1, width=1, height=1)

        self.errors_label = Gtk.Label(label=' ')
        grid.attach(self.errors_label, column=0, row=2, width=4, height=1)

        if move:
            button = Gtk.Button(label='Move')
        else:
            button = Gtk.Button(label='Copy')
        button.set_halign(Gtk.Align.END)
        button.set_valign(Gtk.Align.END)
        button.connect('clicked', self.on_copy_button_clicked)
        grid.attach(button, column=1, row=3, width=1, height=1)

        button = Gtk.Button(label='Cancel')
        button.set_halign(Gtk.Align.START)
        button.set_valign(Gtk.Align.END)
        button.connect('clicked', self.on_cancel_button_clicked)
        grid.attach(button, column=2, row=3, width=1, height=1)

    def on_copy_button_clicked(self, button: Gtk.Button):
        '''On the move/copy button clicked, validate all the fields and display any errors or send
        the response and close the dialog.'''

        errors = []
        index = None
        subindex = None

        subindex_raw = self.subindex_entry.get_text()

        try:
            index = str2int(self.index_entry.get_text())
        except Exception:
            errors.append('ERROR: invalid value in index field')

        if index:
            if index < 0x1000 or index > 0xFFFF:
                errors.append('ERROR: index must be between 0x1000 and 0xFFFF')
            if index in self.eds.indexes and subindex_raw in ['', 'NA']:
                errors.append('ERROR: index already exist')

        if subindex_raw not in ['', 'NA']:
            if index not in self.eds.indexes:
                errors.append('ERROR: index does not exist for new subindex')
            elif self.eds[index].object_type == ObjectType.VAR:
                errors.append('ERROR: cannot add an subindex to a VAR')
            elif subindex in self.eds[index].subindexes:
                errors.append('ERROR: subindex already exist')

            try:
                subindex = str2int(subindex_raw)
            except Exception:
                errors.append('ERROR: invalid value in subindex field')

            if subindex is not None and (subindex < 0 or subindex > 0xFF):
                errors.append('ERROR: subindex must be between 0x0 and 0xFF')

        if errors:  # one or more errors with index/subindex values
            self.errors_label.set_text('\n'.join(errors))
            return

        self._new_index = index
        self._new_subindex = subindex

        self.response(1)
        self.destroy()

    def on_cancel_button_clicked(self, button: Gtk.Button):
        '''On the cancel button clicked, close the dialog.'''

        self.destroy()

    def get_response(self) -> (int, int):
        '''
        Get the custom response from the dialog.

        Returns
        -------
        int
            The index of the new object to add.
        int
            The subindex of the new object to add. Can be set to `None`.
        '''

        return self._new_index, self._new_subindex
