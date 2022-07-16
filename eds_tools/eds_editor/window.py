import os
from gi.repository import Gtk

from ..core import ObjectType, ACCESS_TYPE
from ..core.eds import EDS
from ..core.eds_format import DataType


class AppWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.eds = None
        self.file_path = None

        # Create Notebook
        self.notebook = Gtk.Notebook()
        self.add(self.notebook)
        self.page_focus = 0

        builder = Gtk.Builder()

        path = os.path.dirname(os.path.abspath(__file__))

        # general info page
        builder.add_from_file(path + '/xml/general_info_page.glade')
        page = builder.get_object('general_info_page')
        self.notebook.append_page(page, Gtk.Label.new('General Info'))
        self.file_name = builder.get_object('file_name')
        file_version = builder.get_object('file_version')
        self.file_version = Gtk.Adjustment.new(0, 0, 0xFF, 1, 0, 0)
        file_version.set_adjustment(self.file_version)
        file_revision = builder.get_object('file_revision')
        self.file_revision = Gtk.Adjustment.new(0, 0, 0xFF, 1, 0, 0)
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
        self.general_info_update_button = builder.get_object('general_info_update_button')
        self.general_info_update_button.connect('clicked', self.on_update_button_clicked)
        self.general_info_cancel_button = builder.get_object('general_info_cancel_button')
        self.general_info_cancel_button.connect('clicked', self.on_cancel_button_clicked)

        # object dictionary page
        builder.add_from_file(path + '/xml/object_dictionary_page.glade')
        page = builder.get_object('od_page')
        self.notebook.append_page(page, Gtk.Label.new('Object Dictionary'))
        self.od_treeview = builder.get_object('object_dictionary_tree')
        self.indexes_store = Gtk.TreeStore(str, str, str)
        self.od_treeview.set_model(self.indexes_store)
        for i, column_title in enumerate(['Index', 'Subindex', 'Parameter Name']):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.od_treeview.append_column(column)
        select = self.od_treeview.get_selection()
        select.connect('changed', self.on_tree_selection_changed)
        # data type combobox
        self.obj_data_type = builder.get_object('obj_data_type')
        liststore_obj_data = Gtk.ListStore(str)
        for item in DataType:
            liststore_obj_data.append([item.name])
        self.obj_data_type.set_model(liststore_obj_data)
        self.obj_data_type.set_active(0)
        cellrenderertext = Gtk.CellRendererText()
        self.obj_data_type.pack_start(cellrenderertext, True)
        self.obj_data_type.add_attribute(cellrenderertext, 'text', 0)
        # access type combobox
        self.obj_access_type = builder.get_object('obj_access_type')
        self.liststore_access_type = Gtk.ListStore(str)
        for item in ACCESS_TYPE:
            self.liststore_access_type.append([item])
        self.obj_access_type.set_model(self.liststore_access_type)
        self.obj_access_type.set_active(0)
        cellrenderertext = Gtk.CellRendererText()
        self.obj_access_type.pack_start(cellrenderertext, True)
        self.obj_access_type.add_attribute(cellrenderertext, 'text', 0)
        # object type combobox
        self.obj_type = builder.get_object('obj_type')
        liststore_type = Gtk.ListStore(str)
        for item in ObjectType:
            liststore_type.append([item.name])
        self.obj_type.set_model(liststore_type)
        self.obj_type.set_active(0)
        cellrenderertext = Gtk.CellRendererText()
        self.obj_type.pack_start(cellrenderertext, True)
        self.obj_type.add_attribute(cellrenderertext, 'text', 0)
        # other
        self.obj_parameter_name = builder.get_object('obj_parameter_name')
        self.obj_comment = builder.get_object('obj_comment')
        self.obj_default_value = builder.get_object('obj_default_value')
        self.obj_pdo_mapping = builder.get_object('obj_pdo_mapping')

        # device commisioning page
        builder.add_from_file(path + '/xml/device_commisioning_page.glade')
        page = builder.get_object('device_commisioning_page')
        self.notebook.append_page(page, Gtk.Label.new('Device Commisioning'))
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
        self.canpen_manager = builder.get_object('canpen_manager')

    def on_dc_kbps_selected(self, widget, data=None):
        print(widget.get_label() + ' is selected')

    def on_update_button_clicked(self, button):
        print('update page', self.page_focus)

    def on_cancel_button_clicked(self, button):
        print('cancel page', self.page_focus)

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()

        if not treeiter:
            return

        if model[treeiter][0]:
            index = model[treeiter][0]
            self.selected_obj = self.eds.index(index)
        else:
            index = model[treeiter].parent[0]
            subindex = model[treeiter][1]
            self.selected_obj = self.eds.subindex(index, subindex)

        self.obj_parameter_name.set_text(self.selected_obj['ParameterName'])
        obj_type = self.selected_obj['ObjectType']
        self.obj_type.set_active(list(ObjectType).index(obj_type))
        self.obj_comment.get_buffer().set_text(self.selected_obj.comment)
        if obj_type == ObjectType.VAR:
            data_type = self.selected_obj['DataType']
            self.obj_data_type.set_active(list(DataType).index(data_type))
            access_type = self.selected_obj['AccessType']
            self.obj_access_type.set_active(ACCESS_TYPE.index(access_type))
            self.obj_default_value.set_text(self.selected_obj['DefaultValue'])
            self.obj_pdo_mapping.set_state(self.selected_obj['PDOMapping'])
        else:
            self.obj_data_type.set_active(0)
            self.obj_access_type.set_active(0)
            self.obj_default_value.set_text('')
            self.obj_pdo_mapping.set_state(False)

    def open_file(self, file_path):
        self.file_path = file_path
        self.eds = EDS()
        self.eds.load(file_path)

        for index in self.eds.indexes():
            index_section = self.eds.index(index)
            self.indexes_store.append(None, [index, '', index_section['ParameterName']])
            if index_section['ObjectType'] != ObjectType.VAR:
                for subindex in self.eds.subindexes(index):
                    subindex_section = self.eds.subindex(index, subindex)
                    self.indexes_store.append(
                        self.indexes_store[-1].iter,
                        ['', subindex, subindex_section['ParameterName']]
                    )

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

        device_comm = self.eds.device_commissioning
        if device_comm:
            self.node_name.set_text(device_comm['NodeName'])
            self.node_id.set_value(device_comm['NodeID'])
            self.net_name.set_text(device_comm['NetName'])
            self.network_name.set_value(device_comm['NetworkName'])
            self.canopen_manager.get_state(device_comm['CANopenManager'])
            self.lss_serial_number.get_value(device_comm['LSS_SerialNumber'])

    def save(self, file_path: str = None):
        self.eds.save(file_path)
