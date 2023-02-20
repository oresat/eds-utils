from gi.repository import Gtk

from ...core import BAUD_RATE
from ...core.eds import EDS
from .page import Page


class DeviceCommissioningPage(Page):
    '''A page to edit the device commissioning information of the dcf file.'''

    def __init__(self, eds: EDS):
        super().__init__(eds)

        frame = Gtk.Frame(label='Device Commissioning', margin_top=5, margin_bottom=5,
                          margin_start=5, margin_end=5)
        frame.set_halign(Gtk.Align.START)
        frame.set_valign(Gtk.Align.START)
        self.set_child(frame)

        grid = Gtk.Grid(column_spacing=5, row_spacing=5, row_homogeneous=True,
                        margin_top=5, margin_bottom=5,
                        margin_start=5, margin_end=5)
        frame.set_child(grid)

        label = Gtk.Label.new('Node Name:')
        label.set_halign(Gtk.Align.START)
        self._node_name = Gtk.Entry()
        self._node_name.set_max_length(246)
        grid.attach(label, column=0, row=0, width=1, height=1)
        grid.attach(self._node_name, column=1, row=0, width=2, height=1)

        label = Gtk.Label.new('Network Name:')
        label.set_halign(Gtk.Align.START)
        self._network_name = Gtk.Entry()
        self._network_name.set_max_length(243)
        grid.attach(label, column=0, row=1, width=1, height=1)
        grid.attach(self._network_name, column=1, row=1, width=2, height=1)

        label = Gtk.Label.new('Node ID:')
        label.set_halign(Gtk.Align.START)
        node_id = Gtk.SpinButton()
        node_id.connect('output', self._on_nodeid_output)
        self._node_id = Gtk.Adjustment.new(1, 0x1, 0x7F, 1, 0, 0)
        node_id.set_adjustment(self._node_id)
        grid.attach(label, column=3, row=0, width=1, height=1)
        grid.attach(node_id, column=4, row=0, width=1, height=1)

        label = Gtk.Label.new('Net Number:')
        label.set_halign(Gtk.Align.START)
        net_number = Gtk.SpinButton()
        self._net_number = Gtk.Adjustment.new(0, 0, 0xFFFFFFFF, 1, 0, 0)
        net_number.set_adjustment(self._net_number)
        grid.attach(label, column=3, row=1, width=1, height=1)
        grid.attach(net_number, column=4, row=1, width=1, height=1)

        label = Gtk.Label.new('Baud Rate:')
        label.set_halign(Gtk.Align.START)
        grid.attach(label, column=0, row=2, width=1, height=2)
        self._baud_rate_buttons = []
        first_radio_button = None
        for i in range(len(BAUD_RATE)):
            radio_button = Gtk.CheckButton.new()
            radio_button.set_label(f'{BAUD_RATE[i]} kpbs')

            if first_radio_button is None:  # set the first_radio_button var
                first_radio_button = radio_button
            else:
                radio_button.set_group(first_radio_button)

            column = i % 4  # 0 - 3
            row = i // 4  # 0 or 1
            self._baud_rate_buttons.append(radio_button)
            radio_button.connect('toggled', self._on_baud_rate_changed)
            grid.attach(radio_button, column=1 + column, row=2 + row, width=1, height=1)
        radio_button.set_active(True)  # 1000 kpbs

        label = Gtk.Label.new('LSS Serial Number:')
        label.set_halign(Gtk.Align.START)
        lss_serial_num = Gtk.SpinButton()
        self._lss_serial_num = Gtk.Adjustment.new(0, 0, 0xFFFFFFFF, 1, 0, 0)
        lss_serial_num.set_adjustment(self._lss_serial_num)
        grid.attach(label, column=0, row=4, width=1, height=1)
        grid.attach(lss_serial_num, column=1, row=4, width=1, height=1)

        label = Gtk.Label.new('CANopen Manager:')
        label.set_halign(Gtk.Align.START)
        self._canopen_manager = Gtk.Switch()
        self._canopen_manager.set_halign(Gtk.Align.START)
        self._canopen_manager.set_valign(Gtk.Align.CENTER)
        grid.attach(label, column=2, row=4, width=1, height=1)
        grid.attach(self._canopen_manager, column=3, row=4, width=1, height=1)

        self.refresh()

    def _on_node_name_changed(self, entry: Gtk.Entry):
        self._eds.device_commissioning.node_name = entry.get_text()

    def _on_node_id_changed(self, spin: Gtk.SpinButton):
        self._eds.device_commissioning.node_id = spin.get_value()

    def _on_network_name_changed(self, entry: Gtk.Entry):
        self._eds.device_commissioning.network_name = entry.get_text()

    def _on_net_number_changed(self, spin: Gtk.SpinButton):
        self._eds.device_commissioning.net_number = spin.get_value()

    def _on_baud_rate_changed(self, check: Gtk.CheckButton):
        self._eds.device_commissioning.baud_rate = int(check.get_label()[:-5])

    def _on_lss_serial_number_changed(self, spin: Gtk.SpinButton):
        self._eds.device_commissioning.lss_serialnumber = spin.get_value()

    def _on_canopen_manager_changed(self, switch: Gtk.Switch):
        self._eds.device_commissioning.canopen_manager = switch.get_state()

    def refresh(self):
        '''Refresh the page'''

        device_comm = self._eds.device_commissioning
        self._node_name.set_text(device_comm.node_name)
        self._node_id.set_value(device_comm.node_id)
        self._net_number.set_value(device_comm.net_number)
        self._network_name.set_text(device_comm.network_name)
        index = BAUD_RATE.index(device_comm.baud_rate)
        self._baud_rate_buttons[index].set_active(True)
        self._canopen_manager.set_state(device_comm.canopen_manager)
        self._lss_serial_num.set_value(device_comm.lss_serialnumber)

    def _on_nodeid_output(self, spin: Gtk.SpinButton) -> bool:
        '''Format the Node ID to be a hex value.'''

        spin.props.text = f'0x{int(spin.get_value()):X}'
        return True
