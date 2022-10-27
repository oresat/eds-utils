from datetime import datetime

from gi.repository import Gtk

from ...core.eds import EDS
from .page import Page


class GeneralInfoPage(Page):
    '''A page to edit the general information of the eds / dcf file.'''

    DT_FORMAT = '%Y-%m-%d %I:%M%p'
    '''The eds entry box datetime format'''

    def __init__(self, eds: EDS):
        super().__init__(eds)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_halign(Gtk.Align.START)
        self.set_child(box)

        frame = Gtk.Frame(label='File Info', margin_top=5, margin_bottom=5,
                          margin_start=5, margin_end=5)
        frame.set_valign(Gtk.Align.START)
        box.append(frame)

        grid = Gtk.Grid(column_spacing=5, row_spacing=5, column_homogeneous=True,
                        margin_top=5, margin_bottom=5, margin_start=5, margin_end=5)
        frame.set_child(grid)

        label = Gtk.Label.new('File Name:')
        label.set_halign(Gtk.Align.START)
        self._file_name = Gtk.Entry()
        self._file_name.set_max_length(246)
        self._file_name.set_sensitive(False)
        grid.attach(label, column=0, row=0, width=1, height=1)
        grid.attach(self._file_name, column=1, row=0, width=3, height=1)

        label = Gtk.Label.new('File Version:')
        label.set_halign(Gtk.Align.START)
        file_version = Gtk.SpinButton()
        self._file_version = Gtk.Adjustment.new(0, 0, 255, 0, 0, 0)
        file_version.set_adjustment(self._file_version)
        grid.attach(label, column=0, row=1, width=1, height=1)
        grid.attach(file_version, column=1, row=1, width=1, height=1)

        label = Gtk.Label.new('File Revision:')
        label.set_halign(Gtk.Align.START)
        file_revision = Gtk.SpinButton()
        self._file_revision = Gtk.Adjustment.new(0, 0, 255, 0, 0, 0)
        file_revision.set_adjustment(self._file_revision)
        grid.attach(label, column=2, row=1, width=1, height=1)
        grid.attach(file_revision, column=3, row=1, width=1, height=1)

        label = Gtk.Label.new('Description:')
        label.set_halign(Gtk.Align.START)
        self._description = Gtk.Entry()
        self._description.set_max_length(243)
        grid.attach(label, column=0, row=2, width=1, height=1)
        grid.attach(self._description, column=1, row=2, width=3, height=1)

        label = Gtk.Label.new('Creation Datetime:')
        label.set_halign(Gtk.Align.START)
        self._creation_datetime = Gtk.Entry()
        self._creation_datetime.set_max_length(18)
        self._creation_datetime.set_placeholder_text('yyyy-mm-dd hh:mm(AM|PM)')
        self._creation_datetime.set_sensitive(False)
        grid.attach(label, column=0, row=3, width=1, height=1)
        grid.attach(self._creation_datetime, column=1, row=3, width=2, height=1)

        label = Gtk.Label.new('Creation By:')
        label.set_halign(Gtk.Align.START)
        self._created_by = Gtk.Entry()
        self._created_by.set_max_length(245)
        self._created_by.set_sensitive(False)
        grid.attach(label, column=0, row=4, width=1, height=1)
        grid.attach(self._created_by, column=1, row=4, width=2, height=1)

        label = Gtk.Label.new('Modified Datetime:')
        label.set_halign(Gtk.Align.START)
        self._modification_datetime = Gtk.Entry()
        self._modification_datetime.set_max_length(18)
        self._modification_datetime.set_placeholder_text('yyyy-mm-dd hh:mm(AM|PM)')
        button = Gtk.Button(label='Now')
        button.set_halign(Gtk.Align.START)
        button.connect('clicked', self.on_now_button_clicked)
        grid.attach(label, column=0, row=5, width=1, height=1)
        grid.attach(self._modification_datetime, column=1, row=5, width=2, height=1)
        grid.attach(button, column=3, row=5, width=1, height=1)

        label = Gtk.Label.new('Modified By:')
        label.set_halign(Gtk.Align.START)
        self._modified_by = Gtk.Entry()
        self._modified_by.set_max_length(244)
        grid.attach(label, column=0, row=6, width=1, height=1)
        grid.attach(self._modified_by, column=1, row=6, width=2, height=1)

        frame = Gtk.Frame(label='Device Info', margin_top=5, margin_bottom=5,
                          margin_start=5, margin_end=5)
        frame.set_valign(Gtk.Align.START)
        box.append(frame)

        grid = Gtk.Grid(column_spacing=5, row_spacing=5, column_homogeneous=True,
                        margin_top=5, margin_bottom=5, margin_start=5, margin_end=5)
        frame.set_child(grid)

        label = Gtk.Label.new('Vendor Name:')
        label.set_halign(Gtk.Align.START)
        self._vendor_name = Gtk.Entry()
        self._vendor_name.set_max_length(244)
        grid.attach(label, column=0, row=0, width=1, height=1)
        grid.attach(self._vendor_name, column=1, row=0, width=1, height=1)

        label = Gtk.Label.new('Vendor Number:')
        label.set_halign(Gtk.Align.START)
        vendor_number = Gtk.SpinButton()
        self._vendor_number = Gtk.Adjustment.new(0, 0, 0xFFFFFFFF, 1, 0, 0)
        vendor_number.set_adjustment(self._vendor_number)
        grid.attach(label, column=2, row=0, width=1, height=1)
        grid.attach(vendor_number, column=3, row=0, width=1, height=1)

        label = Gtk.Label.new('Product Name:')
        label.set_halign(Gtk.Align.START)
        self._product_name = Gtk.Entry()
        self._product_name.set_max_length(243)
        grid.attach(label, column=0, row=1, width=1, height=1)
        grid.attach(self._product_name, column=1, row=1, width=1, height=1)

        label = Gtk.Label.new('Product Number:')
        label.set_halign(Gtk.Align.START)
        product_number = Gtk.SpinButton()
        self._product_number = Gtk.Adjustment.new(0, 0, 0xFFFFFFFF, 1, 0, 0)
        product_number.set_adjustment(self._product_number)
        grid.attach(label, column=2, row=1, width=1, height=1)
        grid.attach(product_number, column=3, row=1, width=1, height=1)

        label = Gtk.Label.new('Revision Number:')
        label.set_halign(Gtk.Align.START)
        revision_number = Gtk.SpinButton()
        self._revision_number = Gtk.Adjustment.new(0, 0, 0xFFFFFFFF, 1, 0, 0)
        revision_number.set_adjustment(self._revision_number)
        grid.attach(label, column=0, row=2, width=1, height=1)
        grid.attach(revision_number, column=1, row=2, width=1, height=1)

        label = Gtk.Label.new('Order Code:')
        label.set_halign(Gtk.Align.START)
        self._order_code = Gtk.Entry()
        self._order_code.set_max_length(245)
        grid.attach(label, column=0, row=3, width=1, height=1)
        grid.attach(self._order_code, column=1, row=3, width=1, height=1)

        label = Gtk.Label.new('Simple Boot Up Master:')
        label.set_halign(Gtk.Align.START)
        self._simple_boot_up_master = Gtk.Switch()
        self._simple_boot_up_master.set_halign(Gtk.Align.START)
        self._simple_boot_up_master.set_valign(Gtk.Align.CENTER)
        grid.attach(label, column=0, row=4, width=1, height=1)
        grid.attach(self._simple_boot_up_master, column=1, row=4, width=1, height=1)

        label = Gtk.Label.new('Simple Boot Up Slave:')
        label.set_halign(Gtk.Align.START)
        self._simple_boot_up_slave = Gtk.Switch()
        self._simple_boot_up_slave.set_halign(Gtk.Align.START)
        self._simple_boot_up_slave.set_valign(Gtk.Align.CENTER)
        grid.attach(label, column=0, row=5, width=1, height=1)
        grid.attach(self._simple_boot_up_slave, column=1, row=5, width=1, height=1)

        label = Gtk.Label.new('PDO Mapping Granularity:')
        label.set_halign(Gtk.Align.START)
        self._granularity = Gtk.Adjustment.new(8, 0, 64, 1, 0, 0)
        granularity = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,
                                adjustment=self._granularity)
        granularity.set_digits(0)
        granularity.set_draw_value(True)
        granularity.set_value_pos(Gtk.PositionType.RIGHT)
        granularity.set_sensitive(False)
        grid.attach(label, column=0, row=6, width=1, height=1)
        grid.attach(granularity, column=1, row=6, width=1, height=1)

        label = Gtk.Label.new('Dynamic Channel Support:')
        label.set_halign(Gtk.Align.START)
        self._dynamic_channel_support = Gtk.Switch()
        self._dynamic_channel_support.set_halign(Gtk.Align.START)
        self._dynamic_channel_support.set_valign(Gtk.Align.CENTER)
        grid.attach(label, column=0, row=7, width=1, height=1)
        grid.attach(self._dynamic_channel_support, column=1, row=7, width=1, height=1)

        label = Gtk.Label.new('Group Messaging:')
        label.set_halign(Gtk.Align.START)
        self._group_messaging = Gtk.Switch()
        self._group_messaging.set_halign(Gtk.Align.START)
        self._group_messaging.set_valign(Gtk.Align.CENTER)
        grid.attach(label, column=0, row=8, width=1, height=1)
        grid.attach(self._group_messaging, column=1, row=8, width=1, height=1)

        label = Gtk.Label.new('LSS Supported:')
        label.set_halign(Gtk.Align.START)
        self._lss_support = Gtk.Switch()
        self._lss_support.set_halign(Gtk.Align.START)
        self._lss_support.set_valign(Gtk.Align.CENTER)
        grid.attach(label, column=0, row=9, width=1, height=1)
        grid.attach(self._lss_support, column=1, row=9, width=1, height=1)

        label = Gtk.Label.new('Supported Baud Rates:')
        label.set_halign(Gtk.Align.START)
        self._baudrate_10 = Gtk.CheckButton(label='10 kbps')
        self._baudrate_20 = Gtk.CheckButton(label='20 kbps')
        self._baudrate_50 = Gtk.CheckButton(label='50 kbps')
        self._baudrate_125 = Gtk.CheckButton(label='125 kbps')
        self._baudrate_250 = Gtk.CheckButton(label='250 kbps')
        self._baudrate_500 = Gtk.CheckButton(label='500 kbps')
        self._baudrate_800 = Gtk.CheckButton(label='800 kbps')
        self._baudrate_1000 = Gtk.CheckButton(label='1000 kbps')
        grid.attach(label, column=2, row=2, width=1, height=8)
        grid.attach(self._baudrate_10, column=3, row=2, width=1, height=1)
        grid.attach(self._baudrate_20, column=3, row=3, width=1, height=1)
        grid.attach(self._baudrate_50, column=3, row=4, width=1, height=1)
        grid.attach(self._baudrate_125, column=3, row=5, width=1, height=1)
        grid.attach(self._baudrate_250, column=3, row=6, width=1, height=1)
        grid.attach(self._baudrate_500, column=3, row=7, width=1, height=1)
        grid.attach(self._baudrate_800, column=3, row=8, width=1, height=1)
        grid.attach(self._baudrate_1000, column=3, row=9, width=1, height=1)

        box2 = Gtk.Box(homogeneous=True)
        box.append(box2)

        button = Gtk.Button(label='Update')
        button.set_halign(Gtk.Align.END)
        button.connect('clicked', self.on_update_button_clicked)
        box2.append(button)

        button = Gtk.Button(label='Cancel')
        button.set_halign(Gtk.Align.START)
        button.connect('clicked', self.on_cancel_button_clicked)
        box2.append(button)

        # fillout file info
        file_info = self._eds.file_info
        self._file_name.set_text(file_info.file_name)
        self._file_version.set_value(file_info.file_version)
        self._file_revision.set_value(file_info.file_revision)
        self._description.set_text(file_info.description)
        dt_str = file_info.creation_dt.strftime(self.DT_FORMAT)
        self._creation_datetime.set_text(dt_str)
        self._created_by.set_text(file_info.created_by)
        dt_str = file_info.modification_dt.strftime(self.DT_FORMAT)
        self._modification_datetime.set_text(dt_str)
        self._modified_by.set_text(file_info.modified_by)

        # fillout device info
        device_info = self._eds.device_info
        self._vendor_name.set_text(device_info.vender_name)
        self._vendor_number.set_value(device_info.vender_number)
        self._product_name.set_text(device_info.product_name)
        self._product_number.set_value(device_info.product_number)
        self._revision_number.set_value(device_info.revision_number)
        self._order_code.set_text(device_info.order_code)
        self._baudrate_10.set_active(device_info.baud_rate[10])
        self._baudrate_20.set_active(device_info.baud_rate[20])
        self._baudrate_50.set_active(device_info.baud_rate[50])
        self._baudrate_125.set_active(device_info.baud_rate[125])
        self._baudrate_250.set_active(device_info.baud_rate[250])
        self._baudrate_500.set_active(device_info.baud_rate[500])
        self._baudrate_800.set_active(device_info.baud_rate[800])
        self._baudrate_1000.set_active(device_info.baud_rate[1000])
        self._simple_boot_up_master.set_state(device_info.simple_boot_up_master)
        self._simple_boot_up_slave.set_state(device_info.simple_boot_up_slave)
        self._dynamic_channel_support.set_state(device_info.dynamic_channel_supperted)
        self._group_messaging.set_state(device_info.group_messaging)
        self._lss_support.set_state(device_info.lss_supported)

    def on_now_button_clicked(self, button: Gtk.Button):
        '''Set the modified datetime value in the gui to current time'''

        dt_str = datetime.now().strftime(self.DT_FORMAT)
        self._modification_datetime.set_text(dt_str)

    def on_update_button_clicked(self, button: Gtk.Button):
        '''Save the values from the gui into the data structure'''

        if self._eds is None:
            return

        self._eds_changed = True

        file_info = self._eds.file_info
        device_info = self._eds.device_info

        file_info.file_name = self._file_name.get_text()
        file_info.file_version = int(self._file_version.get_value())
        file_info.file_revision = int(self._file_revision.get_value())
        file_info.description = self._description.get_text()
        dt_str = self._creation_datetime.get_text()
        file_info.creation_dt = datetime.strptime(dt_str, self.DT_FORMAT)
        file_info.created_by = self._created_by.get_text()
        dt_str = self._modification_datetime.get_text()
        file_info.modification_dt = datetime.strptime(dt_str, self.DT_FORMAT)
        file_info.modified_by = self._modified_by.get_text()

        device_info.vendor_name = self._vendor_name.get_text()
        device_info.vender_number = int(self._vendor_number.get_value())
        device_info.product_name = self._product_name.get_text()
        device_info.product_number = int(self._product_number.get_value())
        device_info.revision_number = int(self._revision_number.get_value())
        device_info.order_code = self._order_code.get_text()
        device_info.baud_rate[10] = self._baudrate_10.get_active()
        device_info.baud_rate[20] = self._baudrate_20.get_active()
        device_info.baud_rate[50] = self._baudrate_50.get_active()
        device_info.baud_rate[125] = self._baudrate_125.get_active()
        device_info.baud_rate[250] = self._baudrate_250.get_active()
        device_info.baud_rate[500] = self._baudrate_500.get_active()
        device_info.baud_rate[800] = self._baudrate_800.get_active()
        device_info.baud_rate[1000] = self._baudrate_1000.get_active()
        device_info.simple_boot_up_master = self._simple_boot_up_master.get_state()
        device_info.simple_boot_up_slave = self._simple_boot_up_slave.get_state()
        device_info.dynamic_channel_supperted = self._dynamic_channel_support.get_state()
        device_info.group_messaging = self._group_messaging.get_state()
        device_info.lss_supported = self._lss_support.get_state()

        self._eds.file_info = file_info
        self._eds.device_info = device_info

    def on_cancel_button_clicked(self, button: Gtk.Button):
        '''Reset the values from the gui to the values from the data structure'''

        self._load_eds(self._eds)
