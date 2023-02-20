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

        file_info = self._eds.file_info
        device_info = self._eds.device_info

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
        entry = Gtk.Entry()
        entry.set_max_length(246)
        entry.set_sensitive(False)
        entry.set_text(file_info.file_name)
        grid.attach(label, column=0, row=0, width=1, height=1)
        grid.attach(entry, column=1, row=0, width=3, height=1)

        label = Gtk.Label.new('File Version:')
        label.set_halign(Gtk.Align.START)
        spin = Gtk.SpinButton.new_with_range(0, 255, 1)
        spin.set_value(file_info.file_version)
        spin.connect('value-changed', self._on_file_version_changed)
        grid.attach(label, column=0, row=1, width=1, height=1)
        grid.attach(spin, column=1, row=1, width=1, height=1)

        label = Gtk.Label.new('File Revision:')
        label.set_halign(Gtk.Align.START)
        spin = Gtk.SpinButton.new_with_range(0, 255, 1)
        spin.set_value(file_info.file_revision)
        spin.connect('value-changed', self._on_file_revision_changed)
        grid.attach(label, column=2, row=1, width=1, height=1)
        grid.attach(spin, column=3, row=1, width=1, height=1)

        label = Gtk.Label.new('Description:')
        label.set_halign(Gtk.Align.START)
        entry = Gtk.Entry()
        entry.set_max_length(243)
        entry.set_text(file_info.description)
        entry.connect('changed', self._on_description_changed)
        grid.attach(label, column=0, row=2, width=1, height=1)
        grid.attach(entry, column=1, row=2, width=3, height=1)

        label = Gtk.Label.new('Creation Datetime:')
        label.set_halign(Gtk.Align.START)
        entry = Gtk.Entry()
        entry.set_max_length(18)
        entry.set_placeholder_text('yyyy-mm-dd hh:mm(AM|PM)')
        entry.set_sensitive(False)
        entry.set_text(file_info.creation_dt.strftime(self.DT_FORMAT))
        grid.attach(label, column=0, row=3, width=1, height=1)
        grid.attach(entry, column=1, row=3, width=2, height=1)

        label = Gtk.Label.new('Creation By:')
        label.set_halign(Gtk.Align.START)
        entry = Gtk.Entry()
        entry.set_max_length(245)
        entry.set_sensitive(False)
        entry.set_text(file_info.created_by)
        grid.attach(label, column=0, row=4, width=1, height=1)
        grid.attach(entry, column=1, row=4, width=2, height=1)

        label = Gtk.Label.new('Modified Datetime:')
        label.set_halign(Gtk.Align.START)
        self._modification_dt = Gtk.Entry()
        self._modification_dt.set_max_length(18)
        self._modification_dt.set_placeholder_text('yyyy-mm-dd hh:mm(AM|PM)')
        self._modification_dt.set_sensitive(False)
        self._modification_dt.set_text(file_info.modification_dt.strftime(self.DT_FORMAT))
        button = Gtk.Button(label='Now')
        button.set_halign(Gtk.Align.START)
        button.connect('clicked', self.on_now_button_clicked)
        grid.attach(label, column=0, row=5, width=1, height=1)
        grid.attach(self._modification_dt, column=1, row=5, width=2, height=1)
        grid.attach(button, column=3, row=5, width=1, height=1)

        label = Gtk.Label.new('Modified By:')
        label.set_halign(Gtk.Align.START)
        entry = Gtk.Entry()
        entry.set_max_length(244)
        entry.set_text(file_info.modified_by)
        grid.attach(label, column=0, row=6, width=1, height=1)
        grid.attach(entry, column=1, row=6, width=2, height=1)

        frame = Gtk.Frame(label='Device Info', margin_top=5, margin_bottom=5,
                          margin_start=5, margin_end=5)
        frame.set_valign(Gtk.Align.START)
        box.append(frame)

        grid = Gtk.Grid(column_spacing=5, row_spacing=5, column_homogeneous=True,
                        margin_top=5, margin_bottom=5, margin_start=5, margin_end=5)
        frame.set_child(grid)

        label = Gtk.Label.new('Vendor Name:')
        label.set_halign(Gtk.Align.START)
        entry = Gtk.Entry()
        entry.set_max_length(244)
        entry.set_text(device_info.vendor_name)
        entry.connect('changed', self._on_vendor_name_changed)
        grid.attach(label, column=0, row=0, width=1, height=1)
        grid.attach(entry, column=1, row=0, width=1, height=1)

        label = Gtk.Label.new('Vendor Number:')
        label.set_halign(Gtk.Align.START)
        spin = Gtk.SpinButton.new_with_range(0, 0xFFFFFFFF, 1)
        spin.set_value(device_info.vendor_number)
        spin.connect('value-changed', self._on_vendor_number_changed)
        grid.attach(label, column=2, row=0, width=1, height=1)
        grid.attach(spin, column=3, row=0, width=1, height=1)

        label = Gtk.Label.new('Product Name:')
        label.set_halign(Gtk.Align.START)
        entry = Gtk.Entry()
        entry.set_max_length(243)
        entry.set_text(device_info.product_name)
        entry.connect('changed', self._on_product_name_changed)
        grid.attach(label, column=0, row=1, width=1, height=1)
        grid.attach(entry, column=1, row=1, width=1, height=1)

        label = Gtk.Label.new('Product Number:')
        label.set_halign(Gtk.Align.START)
        spin = Gtk.SpinButton.new_with_range(0, 0xFFFFFFFF, 1)
        spin.set_value(device_info.product_number)
        spin.connect('value-changed', self._on_product_number_changed)
        grid.attach(label, column=2, row=1, width=1, height=1)
        grid.attach(spin, column=3, row=1, width=1, height=1)

        label = Gtk.Label.new('Revision Number:')
        label.set_halign(Gtk.Align.START)
        spin = Gtk.SpinButton.new_with_range(0, 0xFFFFFFFF, 1)
        spin.set_value(device_info.revision_number)
        spin.connect('value-changed', self._on_revision_number_changed)
        grid.attach(label, column=0, row=2, width=1, height=1)
        grid.attach(spin, column=1, row=2, width=1, height=1)

        label = Gtk.Label.new('Order Code:')
        label.set_halign(Gtk.Align.START)
        entry = Gtk.Entry()
        entry.set_max_length(245)
        entry.set_text(device_info.order_code)
        entry.connect('changed', self._on_order_code_changed)
        grid.attach(label, column=0, row=3, width=1, height=1)
        grid.attach(entry, column=1, row=3, width=1, height=1)

        label = Gtk.Label.new('Simple Boot Up Master:')
        label.set_halign(Gtk.Align.START)
        switch = Gtk.Switch()
        switch.set_halign(Gtk.Align.START)
        switch.set_valign(Gtk.Align.CENTER)
        switch.set_active(device_info.simple_boot_up_master)
        switch.connect('state-set', self._on_simple_boot_up_master_changed)
        grid.attach(label, column=0, row=4, width=1, height=1)
        grid.attach(switch, column=1, row=4, width=1, height=1)

        label = Gtk.Label.new('Simple Boot Up Slave:')
        label.set_halign(Gtk.Align.START)
        switch = Gtk.Switch()
        switch.set_halign(Gtk.Align.START)
        switch.set_valign(Gtk.Align.CENTER)
        switch.set_active(device_info.simple_boot_up_slave)
        switch.connect('state-set', self._on_simple_boot_up_slave_changed)
        grid.attach(label, column=0, row=5, width=1, height=1)
        grid.attach(switch, column=1, row=5, width=1, height=1)

        label = Gtk.Label.new('PDO Mapping Granularity:')
        label.set_halign(Gtk.Align.START)
        adjustment = Gtk.Adjustment.new(8, 0, 64, 1, 0, 0)
        granularity = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment)
        granularity.set_digits(0)
        granularity.set_draw_value(True)
        granularity.set_value_pos(Gtk.PositionType.RIGHT)
        granularity.set_sensitive(False)
        grid.attach(label, column=0, row=6, width=1, height=1)
        grid.attach(granularity, column=1, row=6, width=1, height=1)

        label = Gtk.Label.new('Dynamic Channel Support:')
        label.set_halign(Gtk.Align.START)
        switch = Gtk.Switch()
        switch.set_halign(Gtk.Align.START)
        switch.set_valign(Gtk.Align.CENTER)
        switch.set_active(device_info.dynamic_channel_supperted)
        switch.connect('state-set', self._on_dynamic_channel_support_changed)
        grid.attach(label, column=0, row=7, width=1, height=1)
        grid.attach(switch, column=1, row=7, width=1, height=1)

        label = Gtk.Label.new('Group Messaging:')
        label.set_halign(Gtk.Align.START)
        switch = Gtk.Switch()
        switch.set_halign(Gtk.Align.START)
        switch.set_valign(Gtk.Align.CENTER)
        switch.set_active(device_info.group_messaging)
        switch.connect('state-set', self._on_group_messaging_changed)
        grid.attach(label, column=0, row=8, width=1, height=1)
        grid.attach(switch, column=1, row=8, width=1, height=1)

        label = Gtk.Label.new('LSS Supported:')
        label.set_halign(Gtk.Align.START)
        switch = Gtk.Switch()
        switch.set_halign(Gtk.Align.START)
        switch.set_valign(Gtk.Align.CENTER)
        switch.set_active(device_info.lss_supported)
        switch.connect('state-set', self._on_lss_supported_changed)
        grid.attach(label, column=0, row=9, width=1, height=1)
        grid.attach(switch, column=1, row=9, width=1, height=1)

        label = Gtk.Label.new('Supported Baud Rates:')
        label.set_halign(Gtk.Align.START)
        grid.attach(label, column=2, row=1, width=1, height=8)
        check = Gtk.CheckButton(label='10 kbps')
        check.set_active(device_info.baud_rate[10])
        grid.attach(check, column=3, row=2, width=1, height=1)
        check = Gtk.CheckButton(label='20 kbps')
        check.set_active(device_info.baud_rate[20])
        grid.attach(check, column=3, row=3, width=1, height=1)
        check = Gtk.CheckButton(label='50 kbps')
        check.set_active(device_info.baud_rate[50])
        grid.attach(check, column=3, row=4, width=1, height=1)
        check = Gtk.CheckButton(label='125 kbps')
        check.set_active(device_info.baud_rate[125])
        grid.attach(check, column=3, row=5, width=1, height=1)
        check = Gtk.CheckButton(label='250 kbps')
        check.set_active(device_info.baud_rate[250])
        grid.attach(check, column=3, row=6, width=1, height=1)
        check = Gtk.CheckButton(label='500 kbps')
        check.set_active(device_info.baud_rate[500])
        grid.attach(check, column=3, row=7, width=1, height=1)
        check = Gtk.CheckButton(label='800 kbps')
        check.set_active(device_info.baud_rate[800])
        grid.attach(check, column=3, row=8, width=1, height=1)
        check = Gtk.CheckButton(label='1000 kbps')
        check.set_active(device_info.baud_rate[1000])
        grid.attach(check, column=3, row=9, width=1, height=1)

    def on_now_button_clicked(self, button: Gtk.Button):
        self._modification_dt.set_text(datetime.now().strftime(self.DT_FORMAT))

    def _on_file_version_changed(self, spin: Gtk.SpinButton):
        self._eds.file_info.file_version = spin.get_value()

    def _on_file_revision_changed(self, spin: Gtk.SpinButton):
        self._eds.file_info.file_revision = spin.get_value()

    def _on_description_changed(self, entry: Gtk.Entry):
        self._eds.file_info.description = entry.get_text()

    def _on_vendor_name_changed(self, entry: Gtk.Entry):
        self._eds.device_info.vendor_name = entry.get_text()

    def _on_vendor_number_changed(self, spin: Gtk.SpinButton):
        self._eds.device_info.vendor_number = spin.get_value()

    def _on_product_name_changed(self, entry: Gtk.Entry):
        self._eds.device_info.product_name = entry.get_text()

    def _on_product_number_changed(self, spin: Gtk.SpinButton):
        self._eds.device_info.product_number = spin.get_value()

    def _on_revision_number_changed(self, spin: Gtk.SpinButton):
        self._eds.device_info.revision_number = spin.get_value()

    def _on_order_code_changed(self, entry: Gtk.Entry):
        self._eds.device_info.order_code = entry.get_text()

    def _on_simple_boot_up_master_changed(self, switch: Gtk.Switch, state: bool):
        self._eds.device_info.simple_boot_up_master = state

    def _on_simple_boot_up_slave_changed(self, switch: Gtk.Switch, state: bool):
        self._eds.device_info.simple_boot_up_slave = state

    def _on_dynamic_channel_support_changed(self, switch: Gtk.Switch, state: bool):
        self._eds.device_info.dynamic_channel_supperted = state

    def _on_group_messaging_changed(self, switch: Gtk.Switch, state: bool):
        self._eds.device_info.group_messaging = state

    def _on_lss_supported_changed(self, switch: Gtk.Switch, state: bool):
        self._eds.device_info.lss_supported = state
