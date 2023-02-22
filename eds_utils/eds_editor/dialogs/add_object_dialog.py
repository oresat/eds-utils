from gi.repository import Gtk

from ...core import ObjectType, str2int
from ...core.eds import EDS


class AddObjectDialog(Gtk.Dialog):
    '''Gtk Dialog to add a new object to the object dictionary.'''

    def __init__(self, parent: Gtk.Window, eds: EDS):
        '''
        Parameter
        ---------
        parent: Gtk.Window
            The parent window to attach to.
        eds: EDS
            The eds object to check if new object already exist. Dialog does not add new object.
        '''

        super().__init__(title='Add new object', transient_for=parent)

        self._eds = eds
        self._new_index = None
        self._new_subindex = None
        self._new_object_type = None

        box = self.get_content_area()

        grid = Gtk.Grid(column_spacing=5, row_spacing=5, margin_top=5, margin_bottom=5,
                        margin_start=5, margin_end=5)
        box.append(grid)

        label = Gtk.Label(label='Object Type:')
        label.set_halign(Gtk.Align.START)
        self._obj_type = Gtk.DropDown()
        obj_type_list = Gtk.StringList.new(strings=[i.name for i in ObjectType])
        self._obj_type.set_model(obj_type_list)
        self._obj_type.set_selected(0)
        grid.attach(label, column=0, row=0, width=1, height=1)
        grid.attach(self._obj_type, column=1, row=0, width=1, height=1)

        label = Gtk.Label(label='Index:')
        label.set_halign(Gtk.Align.START)
        self._index_entry = Gtk.Entry()
        max_index = eds.indexes[-1]
        self._index_entry.set_text(f'0x{max_index + 1:04X}')
        grid.attach(label, column=0, row=1, width=1, height=1)
        grid.attach(self._index_entry, column=1, row=1, width=1, height=1)

        label = Gtk.Label(label='Subindex (optional):')
        label.set_halign(Gtk.Align.START)
        self._subindex_entry = Gtk.Entry()
        grid.attach(label, column=2, row=1, width=1, height=1)
        grid.attach(self._subindex_entry, column=3, row=1, width=1, height=1)

        self._errors_label = Gtk.Label(label=' ')
        grid.attach(self._errors_label, column=0, row=2, width=4, height=1)

        button = Gtk.Button(label='Add')
        button.set_halign(Gtk.Align.END)
        button.set_valign(Gtk.Align.END)
        button.connect('clicked', self.on_add_button_clicked)
        grid.attach(button, column=1, row=3, width=1, height=1)

        button = Gtk.Button(label='Cancel')
        button.set_halign(Gtk.Align.START)
        button.set_valign(Gtk.Align.END)
        button.connect('clicked', self.on_cancel_button_clicked)
        grid.attach(button, column=2, row=3, width=1, height=1)

        # do this last
        self._obj_type.connect('notify', self.on_object_type_changed)

    def on_object_type_changed(self, drop_down: Gtk.DropDown, active: bool):
        '''If the object_type changes, change editablity of the subindex entry as only variables
        can have subindexes.'''

        object_type = list(ObjectType)[self._obj_type.get_selected()]
        if object_type == ObjectType.VAR:
            self._subindex_entry.set_sensitive(True)
            self._subindex_entry.set_text('')
        else:
            self._subindex_entry.set_sensitive(False)
            self._subindex_entry.set_text('NA')

    def on_add_button_clicked(self, button: Gtk.Button):
        '''On the add button clicked, validate all the fields and display any errors or send the
        response and close the dialog.'''

        errors = []
        index = None
        subindex = None
        object_type = list(ObjectType)[self._obj_type.get_selected()]

        subindex_raw = self._subindex_entry.get_text()

        try:
            index = str2int(self._index_entry.get_text())
        except Exception:
            errors.append('ERROR: invalid value in index field')

        if index:
            if index < 0x1000 or index > 0xFFFF:
                errors.append('ERROR: index must be between 0x1000 and 0xFFFF')
            if index in self._eds.indexes and subindex_raw in ['', 'NA']:
                errors.append('ERROR: index already exist')

        if subindex_raw not in ['', 'NA']:
            if object_type == ObjectType.VAR and index != -1:
                if index not in self._eds.indexes:
                    errors.append('ERROR: index does not exist for new subindex')
                elif self._eds[index].object_type == ObjectType.VAR:
                    errors.append('ERROR: cannot add an subindex to VAR')
                elif subindex in self._eds[index].subindexes:
                    errors.append('ERROR: subindex already exist')

            try:
                subindex = str2int(subindex_raw)
            except Exception:
                errors.append('ERROR: invalid value in subindex field')

            if subindex is not None and (subindex < 0 or subindex > 0xFF):
                errors.append('ERROR: subindex must be between 0x0 and 0xFF')

        if errors:  # one or more errors with index/subindex values
            self._errors_label.set_text('\n'.join(errors))
            return

        self._new_index = index
        self._new_subindex = subindex
        self._new_object_type = object_type

        self.response(1)
        self.destroy()

    def on_cancel_button_clicked(self, button: Gtk.Button):
        '''On the cancel button clicked, close the dialog.'''

        # reset to defaults
        self._obj_type.set_selected(0)
        self._index_entry.set_text('0x1000')
        self._subindex_entry.set_text('')
        self._subindex_entry.set_sensitive(True)

        self._new_index = None
        self._new_subindex = None
        self._new_object_type = None

        self.destroy()

    def get_response(self) -> (int, int, ObjectType):
        '''
        Get the custom response from the dialog.

        Returns
        -------
        int
            The index of the new object to add.
        int
            The subindex of the new object to add. Can be set to `None`.
        ObjectType
            The type of object to add the the index and optional subindex.
        '''

        return self._new_index, self._new_subindex, self._new_object_type
