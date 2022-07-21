from gi.repository import Gtk

from ..core import BAUD_RATE
from ..core.eds import EDS
from ..core.eds_format import DEVICE_COMMISSIONING


class DeviceCommissioningPage(Gtk.ScrolledWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.eds = None

        frame = Gtk.Frame(label='Device Commissioning', margin_top=5, margin_bottom=5,
                          margin_start=5, margin_end=5)
        frame.set_halign(Gtk.Align.START)
        frame.set_valign(Gtk.Align.START)
        self.set_child(frame)

        grid = Gtk.Grid(column_spacing=5, row_spacing=5, margin_top=5, margin_bottom=5,
                        margin_start=5, margin_end=5)
        frame.set_child(grid)

        label = Gtk.Label.new('Node Name:')
        label.set_halign(Gtk.Align.START)
        self.node_name = Gtk.Entry()
        self.node_name.set_max_length(DEVICE_COMMISSIONING['NodeName'].max_length)
        grid.attach(label, column=0, row=0, width=1, height=1)
        grid.attach(self.node_name, column=1, row=0, width=2, height=1)

        label = Gtk.Label.new('Network Name:')
        label.set_halign(Gtk.Align.START)
        self.network_name = Gtk.Entry()
        self.network_name.set_max_length(DEVICE_COMMISSIONING['NetworkName'].max_length)
        grid.attach(label, column=0, row=1, width=1, height=1)
        grid.attach(self.network_name, column=1, row=1, width=2, height=1)

        label = Gtk.Label.new('Node ID:')
        label.set_halign(Gtk.Align.START)
        node_id = Gtk.SpinButton()
        self.node_id = Gtk.Adjustment.new(1, DEVICE_COMMISSIONING['NodeID'].min,
                                          DEVICE_COMMISSIONING['NodeID'].max, 1, 0, 0)
        node_id.set_adjustment(self.node_id)
        grid.attach(label, column=3, row=0, width=1, height=1)
        grid.attach(node_id, column=4, row=0, width=1, height=1)

        label = Gtk.Label.new('Net Number:')
        label.set_halign(Gtk.Align.START)
        net_number = Gtk.SpinButton()
        self.net_number = Gtk.Adjustment.new(0, DEVICE_COMMISSIONING['NetNumber'].min,
                                             DEVICE_COMMISSIONING['NetNumber'].max, 1, 0, 0)
        net_number.set_adjustment(self.net_number)
        grid.attach(label, column=3, row=1, width=1, height=1)
        grid.attach(net_number, column=4, row=1, width=1, height=1)

        label = Gtk.Label.new('Baud Rate:')
        label.set_halign(Gtk.Align.START)
        grid.attach(label, column=0, row=2, width=1, height=2)
        first_radio_button = None
        for i in range(len(BAUD_RATE)):
            radio_button = Gtk.CheckButton.new()
            radio_button.set_label(f'{BAUD_RATE[i]} kpbs')

            if first_radio_button is None:  # set the first_radio_button var
                first_radio_button = radio_button
            else:
                radio_button.set_group(first_radio_button)

            radio_button.connect('toggled', self.on_dc_kbps_selected)
            column = i % 4  # 0 - 3
            row = i // 4  # 0 or 1
            grid.attach(radio_button, column=1 + column, row=2 + row, width=1, height=1)
        radio_button.set_active(True)  # 1000 kpbs

        label = Gtk.Label.new('LSS Serial Number:')
        label.set_halign(Gtk.Align.START)
        lss_serial_num = Gtk.SpinButton()
        self.lss_serial_num = Gtk.Adjustment.new(0, DEVICE_COMMISSIONING['LSS_SerialNumber'].min,
                                                 DEVICE_COMMISSIONING['LSS_SerialNumber'].max,
                                                 1, 0, 0)
        lss_serial_num.set_adjustment(self.lss_serial_num)
        grid.attach(label, column=0, row=4, width=1, height=1)
        grid.attach(lss_serial_num, column=1, row=4, width=1, height=1)

        label = Gtk.Label.new('CANopen Manager:')
        label.set_halign(Gtk.Align.START)
        self.canopen_manager = Gtk.Switch()
        self.canopen_manager.set_halign(Gtk.Align.START)
        self.canopen_manager.set_valign(Gtk.Align.CENTER)
        grid.attach(label, column=2, row=4, width=1, height=1)
        grid.attach(self.canopen_manager, column=3, row=4, width=1, height=1)

    def on_dc_kbps_selected(self, widget, data=None):
        print(widget.get_label() + ' is selected')

    def load_eds(self, eds: EDS):
        self.eds = eds

        device_comm = self.eds.device_commissioning
        if device_comm:
            self.node_name.set_text(device_comm['NodeName'])
            self.node_id.set_value(device_comm['NodeID'])
            self.net_number.set_value(device_comm['NetNumber'])
            self.network_name.set_text(device_comm['NetworkName'])
            self.canopen_manager.set_state(device_comm['CANopenManager'])
            self.lss_serial_num.set_value(device_comm['LSS_SerialNumber'])
        else:
            self.node_name.set_text('')
            self.node_id.set_value(0)
            self.net_number.set_value(0)
            self.network_name.set_text('')
            self.canopen_manager.set_state(False)
            self.lss_serial_num.set_value(0)
