from gi.repository import Gtk

from ..core import DataType, ObjectType, str2int
from ..core.objects import Variable, Array, Record


class AddObjectDialog(Gtk.Dialog):

    def __init__(self, parent, eds):

        super().__init__(title='Add new object', transient_for=parent)

        self.eds = eds

        box = self.get_content_area()

        grid = Gtk.Grid(column_spacing=5, row_spacing=5, margin_top=5, margin_bottom=5,
                        margin_start=5, margin_end=5)
        box.append(grid)

        label = Gtk.Label(label='Object Type:')
        label.set_halign(Gtk.Align.START)
        self.obj_type = Gtk.DropDown()
        obj_type_list = Gtk.StringList.new(strings=[i.name for i in ObjectType])
        self.obj_type.set_model(obj_type_list)
        self.obj_type.set_selected(0)
        grid.attach(label, column=0, row=0, width=1, height=1)
        grid.attach(self.obj_type, column=1, row=0, width=1, height=1)

        label = Gtk.Label(label='Index:')
        label.set_halign(Gtk.Align.START)
        self.index_entry = Gtk.Entry()
        self.index_entry.set_text('0x1000')
        grid.attach(label, column=0, row=1, width=1, height=1)
        grid.attach(self.index_entry, column=1, row=1, width=1, height=1)

        label = Gtk.Label(label='Subindex (optional):')
        label.set_halign(Gtk.Align.START)
        self.subindex_entry = Gtk.Entry()
        grid.attach(label, column=2, row=1, width=1, height=1)
        grid.attach(self.subindex_entry, column=3, row=1, width=1, height=1)

        self.errors_label = Gtk.Label(label=' ')
        grid.attach(self.errors_label, column=0, row=2, width=4, height=1)

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
        self.obj_type.connect('notify', self.on_object_type_changed)

    @property
    def new_object(self):

        object_type = list(ObjectType)[self.obj_type.get_selected()]

        if object_type == ObjectType.VAR:
            obj = Variable()
            data_type = list(DataType)[self.obj_data_type.get_selected()]
            obj.data_type = data_type
            obj.parameter_name = 'New variable'
        elif object_type == ObjectType.ARRAY:
            obj = Array()
            obj.parameter_name = 'New array'
        elif object_type == ObjectType.RECORD:
            obj = Record()
            obj.parameter_name = 'New record'

        return obj

    @property
    def index(self) -> int:

        return self.index_adj.get_value()

    @property
    def subindex(self) -> int:

        return self.subindex_adj.get_value()

    def on_object_type_changed(self, drop_down, flags):

        object_type = list(ObjectType)[self.obj_type.get_selected()]
        if object_type == ObjectType.VAR:
            self.subindex_entry.set_sensitive(True)
            self.subindex_entry.set_text('')
        else:
            self.subindex_entry.set_sensitive(False)
            self.subindex_entry.set_text('NA')

    def on_add_button_clicked(self, button):

        errors = []
        index = -1
        subindex = -1
        object_type = list(ObjectType)[self.obj_type.get_selected()]

        subindex_raw = self.subindex_entry.get_text()

        try:
            index = str2int(self.index_entry.get_text())
        except Exception:
            errors.append('ERROR: invalid value in index field')

        if index != -1:
            if index < 0x1000 or index > 0xFFFF:
                errors.append('ERROR: index must be between 0x1000 and 0xFFFF')
            if index in self.eds.indexes and subindex_raw in ['', 'NA']:
                errors.append('ERROR: index already exist')

        if subindex_raw not in ['', 'NA']:
            if object_type == ObjectType.VAR and index != -1:
                if index not in self.eds.indexes:
                    errors.append('ERROR: index does not exist for new subindex')
                elif self.eds[index].object_type == ObjectType.VAR:
                    errors.append('ERROR: cannot add an subindex to VAR')
                elif subindex in self.eds[index].subindexes:
                    errors.append('ERROR: subindex already exist')

            try:
                subindex = str2int(subindex_raw)
            except Exception:
                errors.append('ERROR: invalid value in subindex field')

            if subindex != -1 and (subindex < 0 or subindex > 0xFF):
                errors.append('ERROR: subindex must be between 0x0 and 0xFF')

        if errors:  # one or more errors with index/subindex values
            self.errors_label.set_text('\n'.join(errors))
            return

        if object_type == ObjectType.VAR:
            obj = Variable()
            obj.parameter_name = 'New variable'
        elif object_type == ObjectType.ARRAY:
            obj = Array()
            obj.parameter_name = 'New array'
        elif object_type == ObjectType.RECORD:
            obj = Record()
            obj.parameter_name = 'New record'

        if subindex != -1:
            self.eds[index][subindex] = obj
        else:
            self.eds[index] = obj

        print(self.eds.indexes)

        self.response(1)
        self.destroy()

    def on_cancel_button_clicked(self, button):

        # reset to defaults
        self.obj_type.set_selected(0)
        self.index_entry.set_text('0x1000')
        self.subindex_entry.set_text('')
        self.subindex_entry.set_sensitive(True)

        self.destroy()
