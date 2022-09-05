from datetime import datetime

from gi.repository import Gtk

from ..core.eds import EDS


class GeneralInfoPage(Gtk.ScrolledWindow):
    DT_FORMAT = '%Y-%m-%d %I:%M%p'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.eds = None

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
        self.file_name = Gtk.Entry()
        self.file_name.set_max_length(246)
        self.file_name.set_sensitive(False)
        grid.attach(label, column=0, row=0, width=1, height=1)
        grid.attach(self.file_name, column=1, row=0, width=3, height=1)

        label = Gtk.Label.new('File Version:')
        label.set_halign(Gtk.Align.START)
        file_version = Gtk.SpinButton()
        self.file_version = Gtk.Adjustment.new(0, 0, 255, 0, 0, 0)
        file_version.set_adjustment(self.file_version)
        grid.attach(label, column=0, row=1, width=1, height=1)
        grid.attach(file_version, column=1, row=1, width=1, height=1)

        label = Gtk.Label.new('File Revision:')
        label.set_halign(Gtk.Align.START)
        file_revision = Gtk.SpinButton()
        self.file_revision = Gtk.Adjustment.new(0, 0, 255, 0, 0, 0)
        file_revision.set_adjustment(self.file_revision)
        grid.attach(label, column=2, row=1, width=1, height=1)
        grid.attach(file_revision, column=3, row=1, width=1, height=1)

        label = Gtk.Label.new('Description:')
        label.set_halign(Gtk.Align.START)
        self.description = Gtk.Entry()
        self.description.set_max_length(243)
        grid.attach(label, column=0, row=2, width=1, height=1)
        grid.attach(self.description, column=1, row=2, width=3, height=1)

        label = Gtk.Label.new('Creation Datetime:')
        label.set_halign(Gtk.Align.START)
        self.creation_datetime = Gtk.Entry()
        self.creation_datetime.set_max_length(18)
        self.creation_datetime.set_placeholder_text('yyyy-mm-dd hh:mm(AM|PM)')
        self.creation_datetime.set_sensitive(False)
        grid.attach(label, column=0, row=3, width=1, height=1)
        grid.attach(self.creation_datetime, column=1, row=3, width=2, height=1)

        label = Gtk.Label.new('Creation By:')
        label.set_halign(Gtk.Align.START)
        self.created_by = Gtk.Entry()
        self.created_by.set_max_length(245)
        self.created_by.set_sensitive(False)
        grid.attach(label, column=0, row=4, width=1, height=1)
        grid.attach(self.created_by, column=1, row=4, width=2, height=1)

        label = Gtk.Label.new('Modified Datetime:')
        label.set_halign(Gtk.Align.START)
        self.modification_datetime = Gtk.Entry()
        self.modification_datetime.set_max_length(18)
        self.modification_datetime.set_placeholder_text('yyyy-mm-dd hh:mm(AM|PM)')
        button = Gtk.Button(label='Now')
        button.set_halign(Gtk.Align.START)
        button.connect('clicked', self.on_now_button_clicked)
        grid.attach(label, column=0, row=5, width=1, height=1)
        grid.attach(self.modification_datetime, column=1, row=5, width=2, height=1)
        grid.attach(button, column=3, row=5, width=1, height=1)

        label = Gtk.Label.new('Modified By:')
        label.set_halign(Gtk.Align.START)
        self.modified_by = Gtk.Entry()
        self.modified_by.set_max_length(244)
        grid.attach(label, column=0, row=6, width=1, height=1)
        grid.attach(self.modified_by, column=1, row=6, width=2, height=1)

        frame = Gtk.Frame(label='Device Info', margin_top=5, margin_bottom=5,
                          margin_start=5, margin_end=5)
        frame.set_valign(Gtk.Align.START)
        box.append(frame)

        grid = Gtk.Grid(column_spacing=5, row_spacing=5, column_homogeneous=True,
                        margin_top=5, margin_bottom=5, margin_start=5, margin_end=5)
        frame.set_child(grid)

        label = Gtk.Label.new('Vendor Name:')
        label.set_halign(Gtk.Align.START)
        self.vendor_name = Gtk.Entry()
        self.vendor_name.set_max_length(244)
        grid.attach(label, column=0, row=0, width=1, height=1)
        grid.attach(self.vendor_name, column=1, row=0, width=1, height=1)

        label = Gtk.Label.new('Vendor Number:')
        label.set_halign(Gtk.Align.START)
        vendor_number = Gtk.SpinButton()
        self.vendor_number = Gtk.Adjustment.new(0, 0, 0xFFFFFFFF, 1, 0, 0)
        vendor_number.set_adjustment(self.vendor_number)
        grid.attach(label, column=2, row=0, width=1, height=1)
        grid.attach(vendor_number, column=3, row=0, width=1, height=1)

        label = Gtk.Label.new('Product Name:')
        label.set_halign(Gtk.Align.START)
        self.product_name = Gtk.Entry()
        self.product_name.set_max_length(243)
        grid.attach(label, column=0, row=1, width=1, height=1)
        grid.attach(self.product_name, column=1, row=1, width=1, height=1)

        label = Gtk.Label.new('Product Number:')
        label.set_halign(Gtk.Align.START)
        product_number = Gtk.SpinButton()
        self.product_number = Gtk.Adjustment.new(0, 0, 0xFFFFFFFF, 1, 0, 0)
        product_number.set_adjustment(self.product_number)
        grid.attach(label, column=2, row=1, width=1, height=1)
        grid.attach(product_number, column=3, row=1, width=1, height=1)

        label = Gtk.Label.new('Revision Number:')
        label.set_halign(Gtk.Align.START)
        revision_number = Gtk.SpinButton()
        self.revision_number = Gtk.Adjustment.new(0, 0, 0xFFFFFFFF, 1, 0, 0)
        revision_number.set_adjustment(self.revision_number)
        grid.attach(label, column=0, row=2, width=1, height=1)
        grid.attach(revision_number, column=1, row=2, width=1, height=1)

        label = Gtk.Label.new('Order Code:')
        label.set_halign(Gtk.Align.START)
        self.order_code = Gtk.Entry()
        self.order_code.set_max_length(245)
        grid.attach(label, column=0, row=3, width=1, height=1)
        grid.attach(self.order_code, column=1, row=3, width=1, height=1)

        label = Gtk.Label.new('Simple Boot Up Master:')
        label.set_halign(Gtk.Align.START)
        self.simple_boot_up_master = Gtk.Switch()
        self.simple_boot_up_master.set_halign(Gtk.Align.START)
        self.simple_boot_up_master.set_valign(Gtk.Align.CENTER)
        grid.attach(label, column=0, row=4, width=1, height=1)
        grid.attach(self.simple_boot_up_master, column=1, row=4, width=1, height=1)

        label = Gtk.Label.new('Simple Boot Up Slave:')
        label.set_halign(Gtk.Align.START)
        self.simple_boot_up_slave = Gtk.Switch()
        self.simple_boot_up_slave.set_halign(Gtk.Align.START)
        self.simple_boot_up_slave.set_valign(Gtk.Align.CENTER)
        grid.attach(label, column=0, row=5, width=1, height=1)
        grid.attach(self.simple_boot_up_slave, column=1, row=5, width=1, height=1)

        label = Gtk.Label.new('PDO Mapping Granularity:')
        label.set_halign(Gtk.Align.START)
        self.granularity = Gtk.Adjustment.new(8, 0, 64, 1, 0, 0)
        granularity = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,
                                adjustment=self.granularity)
        granularity.set_digits(0)
        granularity.set_draw_value(True)
        granularity.set_value_pos(Gtk.PositionType.RIGHT)
        granularity.set_sensitive(False)
        grid.attach(label, column=0, row=6, width=1, height=1)
        grid.attach(granularity, column=1, row=6, width=1, height=1)

        label = Gtk.Label.new('Dynamic Channel Support:')
        label.set_halign(Gtk.Align.START)
        self.dynamic_channel_support = Gtk.Switch()
        self.dynamic_channel_support.set_halign(Gtk.Align.START)
        self.dynamic_channel_support.set_valign(Gtk.Align.CENTER)
        grid.attach(label, column=0, row=7, width=1, height=1)
        grid.attach(self.dynamic_channel_support, column=1, row=7, width=1, height=1)

        label = Gtk.Label.new('Group Messaging:')
        label.set_halign(Gtk.Align.START)
        self.group_messaging = Gtk.Switch()
        self.group_messaging.set_halign(Gtk.Align.START)
        self.group_messaging.set_valign(Gtk.Align.CENTER)
        grid.attach(label, column=0, row=8, width=1, height=1)
        grid.attach(self.group_messaging, column=1, row=8, width=1, height=1)

        label = Gtk.Label.new('LSS Supported:')
        label.set_halign(Gtk.Align.START)
        self.lss_support = Gtk.Switch()
        self.lss_support.set_halign(Gtk.Align.START)
        self.lss_support.set_valign(Gtk.Align.CENTER)
        grid.attach(label, column=0, row=9, width=1, height=1)
        grid.attach(self.lss_support, column=1, row=9, width=1, height=1)

        label = Gtk.Label.new('Supported Baud Rates:')
        label.set_halign(Gtk.Align.START)
        self.baudrate_10 = Gtk.CheckButton(label='10 kbps')
        self.baudrate_20 = Gtk.CheckButton(label='20 kbps')
        self.baudrate_50 = Gtk.CheckButton(label='50 kbps')
        self.baudrate_125 = Gtk.CheckButton(label='125 kbps')
        self.baudrate_250 = Gtk.CheckButton(label='250 kbps')
        self.baudrate_500 = Gtk.CheckButton(label='500 kbps')
        self.baudrate_800 = Gtk.CheckButton(label='800 kbps')
        self.baudrate_1000 = Gtk.CheckButton(label='1000 kbps')
        grid.attach(label, column=2, row=2, width=1, height=8)
        grid.attach(self.baudrate_10, column=3, row=2, width=1, height=1)
        grid.attach(self.baudrate_20, column=3, row=3, width=1, height=1)
        grid.attach(self.baudrate_50, column=3, row=4, width=1, height=1)
        grid.attach(self.baudrate_125, column=3, row=5, width=1, height=1)
        grid.attach(self.baudrate_250, column=3, row=6, width=1, height=1)
        grid.attach(self.baudrate_500, column=3, row=7, width=1, height=1)
        grid.attach(self.baudrate_800, column=3, row=8, width=1, height=1)
        grid.attach(self.baudrate_1000, column=3, row=9, width=1, height=1)

        box2 = Gtk.Box(homogeneous=True)
        box.append(box2)

        button = Gtk.Button(label='Update')
        button.set_halign(Gtk.Align.END)
        box2.append(button)

        button = Gtk.Button(label='Cancel')
        button.set_halign(Gtk.Align.START)
        box2.append(button)

    def on_now_button_clicked(self, button):
        '''Set the modified datetime value in the gui to current time'''

        dt_str = datetime.now().strftime(self.DT_FORMAT)
        self.modification_datetime.set_text(dt_str)

    def load_eds(self, eds: EDS) -> None:
        self.eds = eds

        file_info = self.eds.file_info
        self.file_name.set_text(file_info.file_name)
        self.file_version.set_value(file_info.file_version)
        self.file_revision.set_value(file_info.file_revision)
        self.description.set_text(file_info.description)
        dt_str = file_info.creation_dt.strftime(self.DT_FORMAT)
        self.creation_datetime.set_text(dt_str)
        self.created_by.set_text(file_info.created_by)
        dt_str = file_info.modification_dt.strftime(self.DT_FORMAT)
        self.modification_datetime.set_text(dt_str)
        self.modified_by.set_text(file_info.modified_by)

        device_info = self.eds.device_info
        self.vendor_name.set_text(device_info.vender_name)
        self.vendor_number.set_value(device_info.vender_number)
        self.product_name.set_text(device_info.product_name)
        self.product_number.set_value(device_info.product_number)
        self.revision_number.set_value(device_info.revision_number)
        self.order_code.set_text(device_info.order_code)
        self.baudrate_10.set_active(device_info.baud_rate[10])
        self.baudrate_20.set_active(device_info.baud_rate[20])
        self.baudrate_50.set_active(device_info.baud_rate[50])
        self.baudrate_125.set_active(device_info.baud_rate[125])
        self.baudrate_250.set_active(device_info.baud_rate[250])
        self.baudrate_500.set_active(device_info.baud_rate[500])
        self.baudrate_800.set_active(device_info.baud_rate[800])
        self.baudrate_1000.set_active(device_info.baud_rate[1000])
        self.simple_boot_up_master.set_state(device_info.simple_boot_up_master)
        self.simple_boot_up_slave.set_state(device_info.simple_boot_up_slave)
        self.dynamic_channel_support.set_state(device_info.dynamic_channel_supperted)
        self.group_messaging.set_state(device_info.group_messaging)
        self.lss_support.set_state(device_info.lss_supported)

    def remove_eds(self):
        self.eds = None

    def on_update_button_clicked(self, button):
        '''Save the values from the gui into the data structure'''

        if self.eds is None:
            return

        file_info = self.eds.file_info
        device_info = self.eds.device_info

        file_info.file_name = self.file_name.get_text()
        file_info.file_version = int(self.file_version.get_value())
        file_info.file_revision = int(self.file_revision.get_value())
        file_info.description = self.description.get_text()
        dt_str = self.creation_datetime.get_text()
        file_info.creation_dt = datetime.strptime(dt_str, self.DT_FORMAT)
        file_info.created_by = self.created_by.get_text()
        dt_str = self.modification_datetime.get_text()
        file_info.modification_dt = datetime.strptime(dt_str, self.DT_FORMAT)
        file_info.modified_by = self.modified_by.get_text()

        device_info.vendor_name = self.vendor_name.get_text()
        device_info.vender_number = int(self.vendor_number.get_value())
        device_info.product_name = self.product_name.get_text()
        device_info.product_number = int(self.product_number.get_value())
        device_info.revision_number = int(self.revision_number.get_value())
        device_info.order_code = self.order_code.get_text()
        device_info.baud_rate[10] = self.baudrate_10.get_active()
        device_info.baud_rate[20] = self.baudrate_20.get_active()
        device_info.baud_rate[50] = self.baudrate_50.get_active()
        device_info.baud_rate[125] = self.baudrate_125.get_active()
        device_info.baud_rate[250] = self.baudrate_250.get_active()
        device_info.baud_rate[500] = self.baudrate_500.get_active()
        device_info.baud_rate[800] = self.baudrate_800.get_active()
        device_info.baud_rate[1000] = self.baudrate_1000.get_active()
        device_info.simple_boot_up_master = self.simple_boot_up_master.get_state()
        device_info.simple_boot_up_slave = self.simple_boot_up_slave.get_state()
        device_info.dynamic_channel_supperted = self.dynamic_channel_support.get_state()
        device_info.group_messaging = self.group_messaging.get_state()
        device_info.lss_supported = self.lss_support.get_state()

        self.eds.file_info = file_info
        self.eds.device_info = device_info

    def on_cancel_button_clicked(self, button):
        '''Reset the values from the gui to the values from the data structure'''

        self.load_eds(self.eds)
