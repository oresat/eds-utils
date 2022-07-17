from datetime import datetime
from os.path import abspath, dirname

from gi.repository import Gtk

from ..core.eds import EDS


class GeneralInfoPage:
    def __init__(self):
        self.eds = None

        builder = Gtk.Builder()

        path = dirname(abspath(__file__))
        builder.add_from_file(path + '/xml/general_info_page.glade')
        self.page = builder.get_object('general_info_page')

        self.file_name = builder.get_object('file_name')

        file_version = builder.get_object('file_version')
        self.file_version = Gtk.Adjustment.new(0, 0, 0xFF, 0, 0, 0)
        file_version.set_adjustment(self.file_version)

        file_revision = builder.get_object('file_revision')
        self.file_revision = Gtk.Adjustment.new(0, 0, 0xFF, 0, 0, 0)
        file_revision.set_adjustment(self.file_revision)

        self.eds_version = builder.get_object('eds_version')

        self.description = builder.get_object('description')

        self.creation_datetime = builder.get_object('creation_datetime')

        self.created_by = builder.get_object('created_by')

        self.modification_datetime = builder.get_object('modification_datetime')

        self.modified_by = builder.get_object('modified_by')

        self.vendor_name = builder.get_object('vendor_name')

        vendor_number = builder.get_object('vendor_number')
        self.vendor_number = Gtk.Adjustment.new(0, 0, 0xFFFFFFFF, 1, 0, 0)

        vendor_number.set_adjustment(self.vendor_number)
        self.product_name = builder.get_object('product_name')

        product_number = builder.get_object('product_number')
        self.product_number = Gtk.Adjustment.new(0, 0, 0xFFFFFFFF, 1, 0, 0)

        product_number.set_adjustment(self.product_number)

        revision_number = builder.get_object('revision_number')
        self.revision_number = Gtk.Adjustment.new(0, 0, 0xFF, 1, 0, 0)

        revision_number.set_adjustment(self.revision_number)
        self.order_code = builder.get_object('order_code')
        self.baudrate_10 = builder.get_object('baudrate_10')
        self.baudrate_20 = builder.get_object('baudrate_20')
        self.baudrate_50 = builder.get_object('baudrate_50')
        self.baudrate_125 = builder.get_object('baudrate_125')
        self.baudrate_250 = builder.get_object('baudrate_250')
        self.baudrate_500 = builder.get_object('baudrate_500')
        self.baudrate_800 = builder.get_object('baudrate_800')
        self.baudrate_1000 = builder.get_object('baudrate_1000')

        self.simple_boot_up_master = builder.get_object('simple_boot_up_master')

        self.simple_boot_up_slave = builder.get_object('simple_boot_up_slave')

        granularity = builder.get_object('granularity')
        self.granularity = Gtk.Adjustment.new(8, 0, 64, 1, 0, 0)
        granularity.set_adjustment(self.granularity)

        self.dynamic_channel_support = builder.get_object('dynamic_channel_support')

        self.group_messaging = builder.get_object('group_messaging')

        self.lss_support = builder.get_object('lss_support')

        self.now_button = builder.get_object('modification_now_button')
        self.now_button.connect('clicked', self.on_now_button_clicked)

        update_button = builder.get_object('general_info_update_button')
        update_button.connect('clicked', self.on_update_button_clicked)

        cancel_button = builder.get_object('general_info_cancel_button')
        cancel_button.connect('clicked', self.on_cancel_button_clicked)

    def load_eds(self, eds: EDS) -> None:
        self.eds = eds

        file_info = self.eds.file_info
        self.file_name.set_text(file_info['FileName'])
        self.file_version.set_value(file_info['FileVersion'])
        self.file_revision.set_value(file_info['FileRevision'])
        self.description.set_text(file_info['Description'])
        datetime = file_info['CreationDate'] + ' ' + file_info['CreationTime']
        self.creation_datetime.set_text(datetime)
        self.created_by.set_text(file_info['CreatedBy'])
        datetime = file_info['ModificationDate'] + ' ' + file_info['ModificationTime']
        self.modification_datetime.set_text(datetime)
        self.modified_by.set_text(file_info['ModifiedBy'])

        device_info = self.eds.device_info
        self.vendor_name.set_text(device_info['VendorName'])
        self.vendor_number.set_value(device_info['VendorNumber'])
        self.product_name.set_text(device_info['ProductName'])
        self.product_number.set_value(device_info['ProductNumber'])
        self.revision_number.set_value(device_info['RevisionNumber'])
        self.order_code.set_text(device_info['OrderCode'])
        self.baudrate_10.set_active(device_info['BaudRate_10'])
        self.baudrate_20.set_active(device_info['BaudRate_20'])
        self.baudrate_50.set_active(device_info['BaudRate_50'])
        self.baudrate_125.set_active(device_info['BaudRate_125'])
        self.baudrate_250.set_active(device_info['BaudRate_250'])
        self.baudrate_500.set_active(device_info['BaudRate_500'])
        self.baudrate_800.set_active(device_info['BaudRate_800'])
        self.baudrate_1000.set_active(device_info['BaudRate_1000'])
        self.simple_boot_up_master.set_state(device_info['SimpleBootUpMaster'])
        self.simple_boot_up_slave.set_state(device_info['SimpleBootUpSlave'])
        self.dynamic_channel_support.set_state(device_info['DynamicChannelsSupported'])
        self.group_messaging.set_state(device_info['GroupMessaging'])
        self.lss_support.set_state(device_info['LSS_Supported'])

    def on_update_button_clicked(self, button):
        '''Save the values from the gui into the data structure'''

        if self.eds is None:
            return

        file_info = self.eds.file_info
        device_info = self.eds.device_info

        file_info['FileName'] = self.file_name.get_text()
        file_info['FileVersion'] = int(self.file_version.get_value())
        file_info['FileRevision'] = int(self.file_revision.get_value())
        file_info['Description'] = self.description.get_text()
        dt = self.creation_datetime.get_text().split(' ')
        file_info['CreationDate'] = dt[0]
        file_info['CreationTime'] = dt[1]
        file_info['CreatedBy'] = self.created_by.get_text()
        dt = self.modification_datetime.get_text().split(' ')
        file_info['ModificationDate'] = dt[0]
        file_info['ModificationTime'] = dt[1]
        file_info['ModifiedBy'] = self.modified_by.get_text()

        device_info['VendorName'] = self.vendor_name.get_text()
        device_info['VendorNumber'] = int(self.vendor_number.get_value())
        device_info['ProductName'] = self.product_name.get_text()
        device_info['ProductNumber'] = int(self.product_number.get_value())
        device_info['RevisionNumber'] = int(self.revision_number.get_value())
        device_info['OrderCode'] = self.order_code.get_text()
        device_info['BaudRate_10'] = self.baudrate_10.get_active()
        device_info['BaudRate_20'] = self.baudrate_20.get_active()
        device_info['BaudRate_50'] = self.baudrate_50.get_active()
        device_info['BaudRate_125'] = self.baudrate_125.get_active()
        device_info['BaudRate_250'] = self.baudrate_250.get_active()
        device_info['BaudRate_500'] = self.baudrate_500.get_active()
        device_info['BaudRate_800'] = self.baudrate_800.get_active()
        device_info['SimpleBootUpMaster'] = self.simple_boot_up_master.get_state()
        device_info['SimpleBootUpSlave'] = self.simple_boot_up_slave.get_state()
        device_info['DynamicChannelsSupported'] = self.dynamic_channel_support.get_state()
        device_info['GroupMessaging'] = self.group_messaging.get_state()
        device_info['LSS_Supported'] = self.lss_support.get_state()

        self.eds.file_info = file_info
        self.eds.device_info = device_info

    def on_cancel_button_clicked(self, button):
        '''Reset the values from the gui to the values from the data structure'''

        self.load_eds(self.eds)

    def on_now_button_clicked(self, button):
        '''Set the modified datetime value in the gui to current time'''

        dt_str = datetime.now().strftime('%m-%d-%Y %I:%M%p')
        self.modification_datetime.set_text(dt_str)
