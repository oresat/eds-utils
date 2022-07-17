from os.path import abspath, dirname

from gi.repository import Gtk

from ..core.eds import EDS


class DeviceCommissioningPage:
    def __init__(self):

        self.eds = None
        self.file_path = None

        builder = Gtk.Builder()

        path = dirname(abspath(__file__))
        builder.add_from_file(path + '/xml/device_commissioning_page.glade')
        self.page = builder.get_object('device_commissioning_page')

        self.node_name = builder.get_object('node_name')

        node_id = builder.get_object('node_id')
        self.node_id = Gtk.Adjustment.new(1, 1, 0xFF, 1, 0, 0)
        node_id.set_adjustment(self.node_id)

        self.network_name = builder.get_object('network_name')

        net_number = builder.get_object('net_number')
        self.net_number = Gtk.Adjustment.new(0, 0, 0xFFFFFFFF, 1, 0, 0)
        net_number.set_adjustment(self.net_number)

        # baud rate
        dc_10_kbps = builder.get_object('dc_10_kbps')
        dc_10_kbps.connect('toggled', self.on_dc_kbps_selected)
        dc_20_kbps = builder.get_object('dc_20_kbps')
        dc_20_kbps.connect('toggled', self.on_dc_kbps_selected)
        dc_50_kbps = builder.get_object('dc_50_kbps')
        dc_50_kbps.connect('toggled', self.on_dc_kbps_selected)
        dc_125_kbps = builder.get_object('dc_125_kbps')
        dc_125_kbps.connect('toggled', self.on_dc_kbps_selected)
        dc_250_kbps = builder.get_object('dc_250_kbps')
        dc_250_kbps.connect('toggled', self.on_dc_kbps_selected)
        dc_500_kbps = builder.get_object('dc_500_kbps')
        dc_500_kbps.connect('toggled', self.on_dc_kbps_selected)
        dc_800_kbps = builder.get_object('dc_800_kbps')
        dc_800_kbps.connect('toggled', self.on_dc_kbps_selected)
        dc_1000_kbps = builder.get_object('dc_1000_kbps')
        dc_1000_kbps.connect('toggled', self.on_dc_kbps_selected)

        lss_serial_number = builder.get_object('lss_serial_number')
        self.lss_serial_number = Gtk.Adjustment.new(0, 0, 0xFFFFFFFF, 1, 0, 0)
        lss_serial_number.set_adjustment(self.lss_serial_number)

        self.canopen_manager = builder.get_object('canopen_manager')

    def on_dc_kbps_selected(self, widget, data=None):
        print(widget.get_label() + ' is selected')

    def on_update_button_clicked(self, button):
        print('update page', self.page_focus)

    def on_cancel_button_clicked(self, button):
        print('cancel page', self.page_focus)

    def load_eds(self, eds: EDS):
        self.eds = eds

        device_comm = self.eds.device_commissioning
        if device_comm:
            self.node_name.set_text(device_comm['NodeName'])
            self.node_id.set_value(device_comm['NodeID'])
            self.net_number.set_value(device_comm['NetNumber'])
            self.network_name.set_text(device_comm['NetworkName'])
            self.canopen_manager.set_state(device_comm['CANopenManager'])
            self.lss_serial_number.set_value(device_comm['LSS_SerialNumber'])
        else:
            self.node_name.set_text('')
            self.node_id.set_value(0)
            self.net_number.set_value(0)
            self.network_name.set_text('')
            self.canopen_manager.set_state(False)
            self.lss_serial_number.set_value(0)
