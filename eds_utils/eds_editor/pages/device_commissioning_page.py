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

        button = Gtk.Button(label='Update')
        button.set_halign(Gtk.Align.END)
        button.set_valign(Gtk.Align.END)
        button.connect('clicked', self.on_update_button_clicked)
        grid.attach(button, column=0, row=5, width=2, height=2)

        button = Gtk.Button(label='Cancel')
        button.set_halign(Gtk.Align.START)
        button.set_valign(Gtk.Align.END)
        button.connect('clicked', self.on_cancel_button_clicked)
        grid.attach(button, column=2, row=5, width=2, height=2)

        # a hack to set all the values from the eds
        self.on_cancel_button_clicked(None)

    def on_update_button_clicked(self, button: Gtk.Button):
        '''Update button callback to save changes the device commissioning info.'''

        self._eds_changed = True
        device_comm = self._eds.device_commissioning
        device_comm.node_name = self._node_name.get_text()
        device_comm.node_id = int(self._node_id.get_value())
        device_comm.net_number = int(self._net_number.get_value())
        device_comm.network_name = self._network_name.get_text()
        for i in self._baud_rate_buttons:
            if i.get_active():
                index = self._baud_rate_buttons.index(i)
                device_comm.baud_rate = BAUD_RATE[index]
                break
        self._baud_rate_buttons[index].set_active(True)
        device_comm.canopen_manager = self._canopen_manager.get_state()
        device_comm.lss_serialnumber = int(self._lss_serial_num.get_value())

    def on_cancel_button_clicked(self, button: Gtk.Button):
        '''Cancel button callback to cancel / clear changes the device commissioning info.'''

        device_comm = self._eds.device_commissioning
        self._node_name.set_text(device_comm.node_name)
        self._node_id.set_value(device_comm.node_id)
        self._net_number.set_value(device_comm.net_number)
        self._network_name.set_text(device_comm.network_name)
        index = BAUD_RATE.index(device_comm.baud_rate)
        self._baud_rate_buttons[index].set_active(True)
        self._canopen_manager.set_state(device_comm.canopen_manager)
        self._lss_serial_num.set_value(device_comm.lss_serialnumber)
