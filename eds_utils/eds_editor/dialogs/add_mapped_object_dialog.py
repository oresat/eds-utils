from gi.repository import Gtk

from ...core.objects import Variable
from ...core.eds import EDS


class AddMappedObjectDialog(Gtk.Dialog):
    '''Gtk Dialog to add a new object to the object dictionary.'''

    def __init__(self, parent: Gtk.Window, eds: EDS, index):
        '''
        Parameter
        ---------
        parent: Gtk.Window
            The parent window to attach to.
        eds: EDS
            The eds object to check if new object already exist. Dialog does not add new object.
        '''

        super().__init__(title='Add new mapped object', transient_for=parent)

        self._eds = eds
        self._index = index

        box = self.get_content_area()

        grid = Gtk.Grid(column_spacing=5, row_spacing=5, margin_top=5, margin_bottom=5,
                        margin_start=5, margin_end=5)
        box.append(grid)

        mapped = 0
        for subindex_obj in self._eds[self._index]:
            if self._eds[self._index][0] == subindex_obj:
                continue  # skip
            value = subindex_obj.default_value
            if value == '0x00000000':
                break
            mapped += int(value[-2:], 16)

        free = 64 - mapped

        self._mappable_objs = {}
        for i in self._eds.indexes:
            index = self._eds[i]
            if isinstance(index, Variable):
                if index.pdo_mapping and index.data_type.size <= free:
                    name = f'{index.parameter_name} - {i:X}'
                    self._mappable_objs[name] = index
            else:
                for j in index.subindexes:
                    subindex = index[j]
                    if subindex.pdo_mapping and subindex.data_type.size <= free:
                        name = f'{index.parameter_name} - {subindex.parameter_name} - ' \
                               f'{i:4X}sub{j:02X}'
                        self._mappable_objs[name] = subindex

        label = Gtk.Label.new('Object to Map')
        label.set_halign(Gtk.Align.START)
        self._obj = Gtk.DropDown()
        obj_type_list = Gtk.StringList.new(strings=list(self._mappable_objs.keys()))
        self._obj.set_model(obj_type_list)
        self._obj.set_selected(0)
        grid.attach(label, column=0, row=0, width=1, height=1)
        grid.attach(self._obj, column=1, row=0, width=1, height=1)

        button = Gtk.Button(label='Add')
        button.set_halign(Gtk.Align.END)
        button.set_valign(Gtk.Align.END)
        button.connect('clicked', self.on_add_button_clicked)
        grid.attach(button, column=0, row=1, width=1, height=1)

        button = Gtk.Button(label='Cancel')
        button.set_halign(Gtk.Align.START)
        button.set_valign(Gtk.Align.END)
        button.connect('clicked', self.on_cancel_button_clicked)
        grid.attach(button, column=1, row=1, width=1, height=1)

    def on_add_button_clicked(self, button: Gtk.Button):
        '''On the add button clicked, validate all the fields and display any errors or send the
        response and close the dialog.'''

        name = list(self._mappable_objs.keys())[self._obj.get_selected()]
        obj = self._mappable_objs[name]

        tmp = name.split('-')[-1].replace(' ', '')
        index_hex = tmp[:4]
        subindex_hex = tmp[-2:] if 'sub' in tmp else '00'

        size = obj.data_type.size

        value = f'0x{index_hex}{subindex_hex}{size:02X}'

        for subindex_obj in self._eds[self._index]:
            if subindex_obj.default_value == '0x00000000':
                subindex_obj.default_value = value
                break

        self.response(1)
        self.destroy()

    def on_cancel_button_clicked(self, button: Gtk.Button):
        '''On the cancel button clicked, close the dialog.'''

        self.destroy()
