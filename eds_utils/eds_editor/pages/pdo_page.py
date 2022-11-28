from gi.repository import Gtk, Pango

from ...core import str2int
from ...core.eds import EDS
from ...core.objects import Variable
from .page import Page

RPDO_TRANSMISSION_TYPES = []
for i in range(0, 0xF1):
    RPDO_TRANSMISSION_TYPES.append('Synchronous')
for i in range(0xF1, 0xFE):
    RPDO_TRANSMISSION_TYPES.append('Reserved')
RPDO_TRANSMISSION_TYPES.append('Event-Driven (Manufacture)')
RPDO_TRANSMISSION_TYPES.append('Event-Driven (Device / App)')
'''All valid RPDO transmission types'''

TPDO_TRANSMISSION_TYPES = ['Synchronous (Acycle)']
TPDO_TRANSMISSION_TYPES.append('Synchronous every SYNC')
for i in range(2, 0xF1):
    TPDO_TRANSMISSION_TYPES.append(f'Synchronous every {i} SYNC')
for i in range(0xF1, 0xFC):
    TPDO_TRANSMISSION_TYPES.append('Reserved')
TPDO_TRANSMISSION_TYPES.append('RTC-only (Synchronous)')
TPDO_TRANSMISSION_TYPES.append('RTC-only (Event-Driven)')
TPDO_TRANSMISSION_TYPES.append('Event-Driven (Manufacture)')
TPDO_TRANSMISSION_TYPES.append('Event-Driven (Device / App)')
'''All valid TPDO transmission types'''


class PDOPage(Page):
    '''A page to edit the RPDOs and/or TPDOs of the eds / dcf file.'''

    def __init__(self, eds: EDS, pdo: str):
        super().__init__(eds)

        if pdo.upper() == 'RPDO':
            self._pdo = 'RPDO'
        elif pdo.upper() == 'TPDO':
            self._pdo = 'TPDO'
        else:
            raise ValueError('pdo must be "RPDO" or "TPDO"')

        self._map_name_width = 3

        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)
        box.set_homogeneous(True)
        self.set_child(box)

        self._para_grid = ParaGrid(eds, pdo)
        box.append(self._para_grid)

        self._map_grid = MapGrid(eds, pdo)
        box.append(self._map_grid)

    def refresh(self):
        self._para_grid.refresh()
        self._map_grid.refresh()


class ParaGrid(Gtk.Frame):

    def __init__(self, eds: EDS, pdo: str):
        super().__init__(label=f'{pdo} Commication Parameters', margin_top=5, margin_bottom=5,
                         margin_start=5, margin_end=5)

        if pdo.upper() == 'RPDO':
            self._pdo = 'RPDO'
        elif pdo.upper() == 'TPDO':
            self._pdo = 'TPDO'
        else:
            raise ValueError('pdo must be "RPDO" or "TPDO"')

        self._eds = eds

        scrolled_window = Gtk.ScrolledWindow()
        self.set_child(scrolled_window)

        self._para_grid = Gtk.Grid(column_spacing=10, row_spacing=5, row_homogeneous=True,
                                   margin_start=5, margin_end=5)
        scrolled_window.set_child(self._para_grid)

        self._para_grid.attach(Gtk.Label.new('COB-ID'), column=1, row=0, width=1, height=1)
        self._para_grid.attach(Gtk.Label.new('+NODEID'), column=2, row=0, width=1, height=1)
        self._para_grid.attach(Gtk.Label.new('Valid'), column=3, row=0, width=1, height=1)
        self._para_grid.attach(Gtk.Label.new('RTR Allowed'), column=4, row=0, width=1, height=1)
        label = Gtk.Label.new('Transmission Type')
        self._para_grid.attach(label, column=5, row=0, width=1, height=1)
        label = Gtk.Label.new('Event Time (ms)')
        self._para_grid.attach(label, column=7, row=0, width=1, height=1)
        if self._pdo == 'TPDO':
            label = Gtk.Label.new('Inbit Time (ms)')
            self._para_grid.attach(label, column=6, row=0, width=1, height=1)
            label = Gtk.Label.new('Sync Start Value')
            self._para_grid.attach(label, column=8, row=0, width=1, height=1)

        pdos = self._eds.rpdos if self._pdo == 'RPDO' else self._eds.tpdos
        for i in range(1, pdos + 1):
            label = Gtk.Label.new(f'{pdo} {i}')
            self._para_grid.attach(label, column=0, row=i, width=1, height=1)

            entry = Gtk.Entry()
            entry.set_max_length(5)
            self._para_grid.attach(entry, column=1, row=i, width=1, height=1)

            check = Gtk.CheckButton()
            check.set_halign(Gtk.Align.CENTER)
            self._para_grid.attach(check, column=2, row=i, width=1, height=1)

            check = Gtk.CheckButton()
            check.set_halign(Gtk.Align.CENTER)
            self._para_grid.attach(check, column=3, row=i, width=1, height=1)

            check = Gtk.CheckButton()
            check.set_halign(Gtk.Align.CENTER)
            self._para_grid.attach(check, column=4, row=i, width=1, height=1)

            dropdown = Gtk.DropDown()
            if self._pdo == 'RPDO':
                transmission_list = Gtk.StringList.new(strings=RPDO_TRANSMISSION_TYPES)
            else:
                transmission_list = Gtk.StringList.new(strings=TPDO_TRANSMISSION_TYPES)
            dropdown.set_model(transmission_list)
            self._para_grid.attach(dropdown, column=5, row=i, width=1, height=1)

            spin = Gtk.SpinButton.new_with_range(0, 0xFFFF, 1)
            spin.set_value(0)
            self._para_grid.attach(spin, column=7, row=i, width=1, height=1)

            if self._pdo == 'TPDO':
                spin = Gtk.SpinButton.new_with_range(0, 0xFFFF, 1)
                self._para_grid.attach(spin, column=6, row=i, width=1, height=1)

                spin = Gtk.SpinButton.new_with_range(0, 0xFF, 1)
                self._para_grid.attach(spin, column=8, row=i, width=1, height=1)

        self.refresh()

    def refresh(self):
        start = self._eds.RPDO_COMM_START if self._pdo == 'RPDO' else self._eds.TPDO_COMM_START
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

            self._para_grid.get_child_at(1, pdo).set_text(cob_id)
            self._para_grid.get_child_at(2, pdo).set_active(cob_id_nodeid)
            self._para_grid.get_child_at(3, pdo).set_active(valid)
            self._para_grid.get_child_at(4, pdo).set_active(rtr)
            self._para_grid.get_child_at(5, pdo).set_selected(trans_time)
            self._para_grid.get_child_at(7, pdo).set_value(event_time)
            if self._pdo == 'TPDO':
                self._para_grid.get_child_at(6, pdo).set_value(inhibit_time)
                self._para_grid.get_child_at(8, pdo).set_value(sync_start)

            pdo += 1

            if (self._pdo == 'RPDO' and pdo > self._eds.rpdos) or \
                    (self._pdo == 'TPDO' and pdo > self._eds.tpdos):
                break  # no more PDOs to deal with


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


class MapGrid(Gtk.Frame):

    def __init__(self, eds: EDS, pdo: str):
        super().__init__(label=f'{pdo} Mapping', margin_top=5, margin_bottom=5,
                         margin_start=5, margin_end=5)

        if pdo.upper() == 'RPDO':
            self._pdo = 'RPDO'
        elif pdo.upper() == 'TPDO':
            self._pdo = 'TPDO'
        else:
            raise ValueError('pdo must be "RPDO" or "TPDO"')

        self._eds = eds

        self._map_name_width = 3

        scrolled_window = Gtk.ScrolledWindow()
        self.set_child(scrolled_window)

        self._map_grid = Gtk.Grid(column_spacing=5, row_spacing=5, column_homogeneous=True,
                                  row_homogeneous=True, margin_start=5, margin_end=5)
        scrolled_window.set_child(self._map_grid)

        for i in range(8):
            label = Gtk.Label.new(f'Byte {i}')
            col = self._map_name_width + i * 8
            self._map_grid.attach(label, column=col, row=0, width=8, height=1)

        pdos = self._eds.rpdos if self._pdo == 'RPDO' else self._eds.tpdos
        for i in range(1, pdos + 1):
            label = Gtk.Label.new(f'{pdo} {i}')
            self._map_grid.attach(label, column=0, row=i, width=self._map_name_width, height=1)
            button = Gtk.Button(label='Add')
            button.set_icon_name('list-add-symbolic')
            button.connect('clicked', self._on_add_clicked)
            col = self._map_name_width + 64
            self._map_grid.attach(button, column=col, row=i, width=2, height=1)

            button = Gtk.Button(label='Remove')
            button.set_icon_name('list-remove-symbolic')
            button.connect('clicked', self._on_remove_clicked)
            col = self._map_name_width + 64 + 2
            self._map_grid.attach(button, column=col, row=i, width=2, height=1)

        self.refresh()

    def mappable_rpdos_names(self) -> dict:
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
        mappable_objs = self.mappable_rpdos_names()

        start = self._eds.RPDO_PARA_START if self._pdo == 'RPDO' else self._eds.TPDO_PARA_START
        stop = start + 0x200

        pdo = 1
        for i in range(start, stop):
            pos = 1
            for j in range(1, len(self._eds[i])):
                label = Gtk.Label()
                label.set_ellipsize(Pango.EllipsizeMode.END)
                button = Gtk.Button.new()
                button.set_child(label)

                value = self._eds[i][j].default_value

                index, subindex, size = pdo_mapping_fields(value)

                if index == 0:
                    break  # move to next pdo

                if isinstance(self._eds[index], Variable):
                    obj = self._eds[index]
                else:
                    obj = self._eds[index][subindex]

                label.set_text(mappable_objs[obj])

                col = self._map_name_width + (pos - 1) * 8
                self._map_grid.attach(button, column=col, row=pdo, width=size, height=1)

                pos += size // 8

            add_col = self._map_name_width + 64
            remove_col = self._map_name_width + 64 + 2
            if pos > 8:
                self._map_grid.get_child_at(add_col, pdo).set_sensitive(False)
                self._map_grid.get_child_at(remove_col, pdo).set_sensitive(True)
            elif pos == 1:
                self._map_grid.get_child_at(add_col, pdo).set_sensitive(True)
                self._map_grid.get_child_at(remove_col, pdo).set_sensitive(False)
            else:
                self._map_grid.get_child_at(add_col, pdo).set_sensitive(True)
                self._map_grid.get_child_at(remove_col, pdo).set_sensitive(True)

            pdo += 1

            if (self._pdo == 'RPDO' and pdo > self._eds.rpdos) or \
                    (self._pdo == 'TPDO' and pdo > self._eds.tpdos):
                break  # no more PDOs to deal with

    def _on_add_clicked(self, button: Gtk.Button):
        col, row, width, height = self._map_grid.query_child(button)

    def _on_remove_clicked(self, button: Gtk.Button):
        col, row, width, height = self._map_grid.query_child(button)
        col -= 4
        while col > self._map_name_width:
            col -= 8
            child = self._map_grid.get_child_at(col, row)
            if child is not None:
                col, row, width, height = self._map_grid.query_child(child)
                self._map_grid.remove(child)
                index = 0x1600 if self._pdo == 'RPDO' else 0x1A00
                subindex = (col - self._map_name_width) // 8 + 1
                self._eds[index][subindex].default_value = 0x00000000
                break
