from gi.repository import Gtk, Pango

from ...core import str2int, TPDO_TRANSMISSION_TYPES, RPDO_TRANSMISSION_TYPES
from ...core.eds import EDS
from ...core.objects import Variable
from ..dialogs.add_mapped_object_dialog import AddMappedObjectDialog
from .page import Page


def pdo_mapping_fields(value: str) -> (int, int, int):
    '''
    Pull out the values from a PDO mapping value.

    Parameters
    ----------
    value: str
        THe PDO mapping value

    Returns
    -------
    int
        Mapped object index
    int
        Mapped object subindex
    int
        Mapped object size in bits
    '''

    index = str2int(value[:6])
    subindex = str2int(f'0x{value[6:8]}')
    size = str2int(f'0x{value[8:]}')

    return index, subindex, size


class PDOPage(Page):
    '''A page to edit the RPDOs and/or TPDOs of the eds / dcf file.'''

    def __init__(self, eds: EDS, parent_window: Gtk.Window, pdo: str):
        super().__init__(eds)

        self._parent_window = parent_window

        if pdo.upper() == 'RPDO':
            self._pdo = 'RPDO'
        elif pdo.upper() == 'TPDO':
            self._pdo = 'TPDO'
        else:
            raise ValueError('pdo must be "RPDO" or "TPDO"')

        self._grid = ParaGrid(eds, parent_window, pdo)
        self.set_child(self._grid)

    def refresh(self):
        self._grid.refresh()


class ParaGrid(Gtk.Frame):

    # colum indexes and widths
    _NAME_I = 0
    _NAME_W = 4
    _COB_I = _NAME_I + _NAME_W
    _COB_W = 4
    _PLUS_I = _COB_I + _COB_W
    _PLUS_W = 4
    _VALID_I = _PLUS_I + _PLUS_W
    _VALID_W = 3
    _RTR_I = _VALID_I + _VALID_W
    _RTR_W = 4
    _TRANS_I = _RTR_I + _RTR_W
    _TRANS_W = 10
    _INBIT_I = _TRANS_I + _TRANS_W
    _INBIT_W = 6
    _EVENT_I = _INBIT_I + _INBIT_W
    _EVENT_W = 6
    _SYNC_I = _EVENT_I + _EVENT_W
    _SYNC_W = 6
    _BYTE_W = 8
    _BYTES_I = _SYNC_I + _SYNC_W
    _BYTES_W = _BYTE_W * 8
    _ADD_I = _BYTES_I + _BYTES_W
    _ADD_W = 2
    _REMOVE_I = _ADD_I + _ADD_W
    _REMOVE_W = 2

    def __init__(self, eds: EDS, parent_window, pdo: str):
        super().__init__(label=f'{pdo}', margin_top=5, margin_bottom=5, margin_start=5,
                         margin_end=5)

        self._parent_window = parent_window
        self._eds = eds

        if pdo.upper() == 'RPDO':
            self._pdo = 'RPDO'
        elif pdo.upper() == 'TPDO':
            self._pdo = 'TPDO'
        else:
            raise ValueError('pdo must be "RPDO" or "TPDO"')

        scrolled_window = Gtk.ScrolledWindow()
        self.set_child(scrolled_window)

        self._grid = Gtk.Grid(column_spacing=5, row_spacing=5, column_homogeneous=True,
                              row_homogeneous=True, margin_start=5, margin_end=5)
        self._grid.set_valign(Gtk.Align.START)
        scrolled_window.set_child(self._grid)

        self._grid.attach(Gtk.Label.new('COB-ID'), self._COB_I, 0, self._COB_W, 1)
        self._grid.attach(Gtk.Label.new('+$NODEID'), self._PLUS_I, 0, self._PLUS_W, 1)
        self._grid.attach(Gtk.Label.new('Valid'), self._VALID_I, 0, self._VALID_W, 1)
        self._grid.attach(Gtk.Label.new('RTR Allowed'), self._RTR_I, 0, self._RTR_W, 1)
        label = Gtk.Label.new('Transmission Type')
        self._grid.attach(label, self._TRANS_I, 0, self._TRANS_W, 1)
        label = Gtk.Label.new('Event Time (ms)')
        self._grid.attach(label, self._EVENT_I, 0, self._EVENT_W, 1)
        if self._pdo == 'TPDO':
            label = Gtk.Label.new('Inbit Time (ms)')
            self._grid.attach(label, self._INBIT_I, 0, self._INBIT_W, 1)
            label = Gtk.Label.new('Sync Start Value')
            self._grid.attach(label, self._SYNC_I, 0, self._SYNC_W, 1)
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
        box.set_homogeneous(True)

        for i in range(8):
            label = Gtk.Label.new(f'Byte {i}')
            col = self._BYTES_I + i * 8
            self._grid.attach(label, col, 0, self._BYTE_W, 1)

        pdos = self._eds.rpdos if self._pdo == 'RPDO' else self._eds.tpdos
        for i in range(1, pdos + 1):
            label = Gtk.Label.new(f'{self._pdo} {i}')
            self._grid.attach(label, self._NAME_I, i, self._NAME_W, 1)

            entry = Gtk.Entry()
            entry.set_max_length(5)
            self._grid.attach(entry, self._COB_I, i, self._COB_W, 1)

            check = Gtk.CheckButton()
            check.set_halign(Gtk.Align.CENTER)
            self._grid.attach(check, self._PLUS_I, i, self._PLUS_W, 1)

            check = Gtk.CheckButton()
            check.set_halign(Gtk.Align.CENTER)
            self._grid.attach(check, self._VALID_I, i, self._VALID_W, 1)

            check = Gtk.CheckButton()
            check.set_halign(Gtk.Align.CENTER)
            self._grid.attach(check, self._RTR_I, i, self._RTR_W, 1)

            dropdown = Gtk.DropDown()
            if self._pdo == 'RPDO':
                transmission_list = Gtk.StringList.new(strings=RPDO_TRANSMISSION_TYPES)
            else:
                transmission_list = Gtk.StringList.new(strings=TPDO_TRANSMISSION_TYPES)
            dropdown.set_model(transmission_list)
            self._grid.attach(dropdown, self._TRANS_I, i, self._TRANS_W, 1)

            spin = Gtk.SpinButton.new_with_range(0, 0xFFFF, 1)
            spin.set_value(0)
            self._grid.attach(spin, self._EVENT_I, i, self._EVENT_W, 1)

            if self._pdo == 'TPDO':
                spin = Gtk.SpinButton.new_with_range(0, 0xFFFF, 1)
                self._grid.attach(spin, self._INBIT_I, i, self._INBIT_W, 1)

                spin = Gtk.SpinButton.new_with_range(0, 0xFF, 1)
                self._grid.attach(spin, self._SYNC_I, i, self._SYNC_W, 1)

            button = Gtk.Button(label='Add')
            button.set_icon_name('list-add-symbolic')
            button.connect('clicked', self._on_add_clicked)
            self._grid.attach(button, self._ADD_I, i, self._ADD_W, 1)

            button = Gtk.Button(label='Remove')
            button.set_icon_name('list-remove-symbolic')
            button.connect('clicked', self._on_remove_clicked)
            self._grid.attach(button, self._REMOVE_I, i, self._REMOVE_W, 1)

        self.refresh()

    def _mappable_rpdos_names(self) -> dict:
        objs = {}

        for i in self._eds.indexes:
            index = self._eds[i]
            if isinstance(index, Variable):
                if index.pdo_mapping:
                    objs[index] = f'{index.parameter_name} - {i:X}'
                continue
            else:
                for j in index.subindexes:
                    subindex = index[j]
                    if subindex.pdo_mapping:
                        objs[subindex] = f'{subindex.parameter_name} - {i:4X}sub{j:02X}'

        return objs

    def refresh(self):
        mappable_objs = self._mappable_rpdos_names()
        start = EDS.RPDO_COMM_START if self._pdo == 'RPDO' else EDS.TPDO_COMM_START
        map_start = EDS.RPDO_PARA_START if self._pdo == 'RPDO' else EDS.TPDO_PARA_START
        stop = start + 0x200

        pdo = 1
        for i in range(start, stop):
            cob_id_raw = self._eds[i][1].default_value.replace(' ', '').split('+')
            cob_id_int = str2int(cob_id_raw[0])
            cob_id = f'0x{(cob_id_int & 0xFFF):X}'
            cob_id_nodeid = len(cob_id_raw) == 2
            valid = not bool(cob_id_int & 0x80000000)
            rtr = not bool(cob_id_int & 0x40000000)
            trans_time = str2int(self._eds[i][2].default_value)
            event_time = str2int(self._eds[i][5].default_value)
            if self._pdo == 'TPDO':
                inhibit_time = str2int(self._eds[i][3].default_value)
                sync_start = str2int(self._eds[i][6].default_value)

            self._grid.get_child_at(self._COB_I, pdo).set_text(cob_id)
            self._grid.get_child_at(self._PLUS_I, pdo).set_active(cob_id_nodeid)
            self._grid.get_child_at(self._VALID_I, pdo).set_active(valid)
            self._grid.get_child_at(self._RTR_I, pdo).set_active(rtr)
            self._grid.get_child_at(self._TRANS_I, pdo).set_selected(trans_time)
            self._grid.get_child_at(self._EVENT_I, pdo).set_value(event_time)
            if self._pdo == 'TPDO':
                self._grid.get_child_at(self._INBIT_I, pdo).set_value(inhibit_time)
                self._grid.get_child_at(self._SYNC_I, pdo).set_value(sync_start)

            index = map_start + pdo - 1

            # remove any old childs
            for subindex in range(0, len(self._eds[index]) - 1):
                col = self._BYTES_I + subindex * 8
                child = self._grid.get_child_at(col, pdo)
                if child is not None:
                    self._grid.remove(child)

            size_offset = 0
            for subindex in range(1, len(self._eds[index])):
                label = Gtk.Label()
                label.set_ellipsize(Pango.EllipsizeMode.END)
                button = Gtk.Button.new()
                button.set_child(label)

                value = self._eds[index][subindex].default_value
                if value == '0x00000000':
                    break

                obj_index, obj_subindex, obj_size = pdo_mapping_fields(value)

                if isinstance(self._eds[obj_index], Variable):
                    obj = self._eds[obj_index]
                else:
                    obj = self._eds[obj_index][obj_subindex]

                label.set_text(mappable_objs[obj])

                col = self._BYTES_I + size_offset
                self._grid.attach(button, col, pdo, obj_size, 1)

                size_offset += obj_size

            add_button = self._grid.get_child_at(self._ADD_I, pdo)
            remove_button = self._grid.get_child_at(self._REMOVE_I, pdo)
            if size_offset == 64:
                add_button.set_sensitive(False)
                remove_button.set_sensitive(True)
            elif size_offset == 0:
                add_button.set_sensitive(True)
                remove_button.set_sensitive(False)
            else:
                add_button.set_sensitive(True)
                remove_button.set_sensitive(True)

            pdo += 1

            if (self._pdo == 'RPDO' and pdo > self._eds.rpdos) or \
                    (self._pdo == 'TPDO' and pdo > self._eds.tpdos):
                break  # no more PDOs to deal with

    def _on_add_clicked(self, button: Gtk.Button):
        col, row, width, height = self._grid.query_child(button)
        start = EDS.RPDO_PARA_START if self._pdo == 'RPDO' else EDS.TPDO_PARA_START
        index = start + row - 1

        dialog = AddMappedObjectDialog(self._parent_window, self._eds, index)
        dialog.connect('response', self.add_mapped_object_response)
        dialog.show()

    def add_mapped_object_response(self, dialog: Gtk.Dialog, response: int):
        '''Parses the response to the add mapped object dialog.'''

        self._eds_changed = True
        self.refresh()

    def _on_remove_clicked(self, button: Gtk.Button):

        self._eds_changed = True

        col, row, width, height = self._grid.query_child(button)

        start = EDS.RPDO_PARA_START if self._pdo == 'RPDO' else EDS.TPDO_PARA_START
        index = start + row - 1
        for subindex in range(len(self._eds[index]) - 1, 0, -1):
            if self._eds[index][subindex].default_value != '0x00000000':
                self._eds[index][subindex].default_value = '0x00000000'
                break

        self.refresh()
