import math as m

from gi.repository import Gtk

from ...core.eds import EDS
from ...core import DataType, ObjectType, AccessType


class ObjectGrid(Gtk.Grid):
    '''Common object gird for pages to use'''

    def __init__(self, eds: EDS, parameter_name_cb):
        super().__init__(column_spacing=5, row_spacing=5,
                         column_homogeneous=True, row_homogeneous=True,
                         margin_top=5, margin_bottom=5, margin_start=5, margin_end=5)

        self._eds = eds
        self._parameter_name_cb = parameter_name_cb
        self._index = None
        self._subindex = None

        label = Gtk.Label.new('Parameter Name:')
        label.set_halign(Gtk.Align.START)
        self._obj_parameter_name = Gtk.Entry()
        self._obj_parameter_name.set_max_length(241)
        self._obj_parameter_name.connect('changed', self._on_parametere_name_changed)
        self.attach(label, column=0, row=0, width=1, height=1)
        self.attach(self._obj_parameter_name, column=1, row=0, width=3, height=1)

        label = Gtk.Label.new('Denotation (DCF only):')
        label.set_halign(Gtk.Align.START)
        self._obj_denotation = Gtk.Entry()
        self._obj_denotation.set_max_length(241)
        self._obj_denotation.connect('changed', self._on_obj_denotation_changed)
        if self._eds.file_info.file_name.endswith('.eds'):
            label.hide()
            self._obj_denotation.hide()
        self.attach(label, column=0, row=1, width=1, height=1)
        self.attach(self._obj_denotation, column=1, row=1, width=3, height=1)

        label = Gtk.Label.new('Object Type:')
        label.set_halign(Gtk.Align.START)
        self._obj_type = Gtk.DropDown()
        self._obj_type.set_sensitive(False)
        obj_type_list = Gtk.StringList.new(strings=[i.name for i in ObjectType])
        self._obj_type.set_model(obj_type_list)
        self._obj_type.set_selected(0)
        self.attach(label, column=0, row=2, width=1, height=1)
        self.attach(self._obj_type, column=1, row=2, width=1, height=1)

        label = Gtk.Label.new('Access Type:')
        label.set_halign(Gtk.Align.START)
        self._obj_access_type = Gtk.DropDown()
        access_type_list = Gtk.StringList.new(strings=[i.name for i in AccessType])
        self._obj_access_type.set_model(access_type_list)
        self._obj_access_type.set_selected(0)
        self._obj_access_type.connect('notify::selected-item', self._on_obj_access_type_changed)
        self.attach(label, column=2, row=2, width=1, height=1)
        self.attach(self._obj_access_type, column=3, row=2, width=1, height=1)

        label = Gtk.Label.new('Comment:')
        label.set_halign(Gtk.Align.START)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_has_frame(True)
        text_view = Gtk.TextView()
        self._obj_comment = text_view.get_buffer()
        self._obj_comment.connect('changed', self._on_obj_comment_changed)
        scrolled_window.set_child(text_view)
        self.attach(label, column=0, row=3, width=1, height=5)
        self.attach(scrolled_window, column=1, row=3, width=3, height=5)

        label = Gtk.Label.new('Data Type:')
        label.set_halign(Gtk.Align.START)
        self._obj_data_type = Gtk.DropDown()
        data_type_list = Gtk.StringList.new(strings=[i.name for i in DataType])
        self._obj_data_type.set_model(data_type_list)
        self._obj_data_type.set_selected(0)
        self._obj_data_type.connect('notify::selected-item', self._on_obj_data_type_changed)
        self.attach(label, column=0, row=8, width=1, height=1)
        self.attach(self._obj_data_type, column=1, row=8, width=1, height=1)

        label = Gtk.Label.new('PDO Mapping:')
        label.set_halign(Gtk.Align.START)
        self._obj_pdo_mapping = Gtk.Switch()
        self._obj_pdo_mapping.set_halign(Gtk.Align.START)
        self._obj_pdo_mapping.set_valign(Gtk.Align.CENTER)
        self._obj_pdo_mapping.connect('state-set', self._on_obj_pdo_mapping_changed)
        self.attach(label, column=2, row=8, width=1, height=1)
        self.attach(self._obj_pdo_mapping, column=3, row=8, width=1, height=1)

        label = Gtk.Label.new('Default Value:')
        label.set_halign(Gtk.Align.START)
        self._obj_default_value = Gtk.Entry()
        self._obj_default_value.connect('changed', self._on_obj_default_value_changed)
        self.attach(label, column=0, row=9, width=1, height=1)
        self.attach(self._obj_default_value, column=1, row=9, width=2, height=1)

        self._obj_default_value_len_label = Gtk.Label.new('(Length: 0)')
        self._obj_default_value_len_label.set_halign(Gtk.Align.START)
        self._obj_default_value_len_label.hide()
        self.attach(self._obj_default_value_len_label, column=3, row=9, width=1, height=1)

        label = Gtk.Label.new('Low Limit:')
        label.set_halign(Gtk.Align.START)
        self._obj_low_limit = Gtk.Entry()
        self._obj_low_limit.connect('changed', self._on_obj_low_limit_changed)
        self.attach(label, column=0, row=10, width=1, height=1)
        self.attach(self._obj_low_limit, column=1, row=10, width=1, height=1)

        label = Gtk.Label.new('High Limit:')
        label.set_halign(Gtk.Align.START)
        self._obj_high_limit = Gtk.Entry()
        self._obj_high_limit.connect('changed', self._on_obj_high_limit_changed)
        self.attach(label, column=2, row=10, width=1, height=1)
        self.attach(self._obj_high_limit, column=3, row=10, width=1, height=1)

        label = Gtk.Label.new('Storage Location (CANopenNode):')
        label.set_halign(Gtk.Align.START)
        self._obj_storage_loc = Gtk.DropDown()
        if self._eds.storage_locations:
            str_list = Gtk.StringList.new(strings=self._eds.storage_locations)
            self._obj_storage_loc.set_model(str_list)
            self._obj_storage_loc.set_selected(0)
            self._obj_storage_loc.connect('notify::selected-item',
                                          self._on_obj_storage_loc_changed)
        else:
            label.hide()
            self._obj_storage_loc.hide()
        self.attach(label, column=0, row=11, width=1, height=1)
        self.attach(self._obj_storage_loc, column=1, row=11, width=1, height=1)

    def load_object(self, index: int, subindex: int = None):
        '''When value is selected in the treeview, changed the current selected object.'''

        self._index = index
        self._subindex = subindex
        self._selected_obj = self._eds[index] if subindex is None else self._eds[index][subindex]

        # reset these
        self._obj_data_type.set_sensitive(True)
        self._obj_storage_loc.set_sensitive(True)
        self._obj_default_value_len_label.hide()

        # data_type set sensitivity
        if self._eds[index].object_type in [ObjectType.ARRAY, ObjectType.RECORD]:
            if subindex == 0:
                self._obj_data_type.set_sensitive(False)
            self._obj_storage_loc.set_sensitive(False)
        if self._eds[index].object_type == ObjectType.ARRAY:
            self._obj_data_type.set_sensitive(False)

        if self._selected_obj.object_type == ObjectType.ARRAY:
            self._obj_data_type.show()
            self._obj_access_type.hide()
            self._obj_pdo_mapping.hide()
            self._obj_default_value.hide()
            self._obj_low_limit.hide()
            self._obj_high_limit.hide()
        elif self._selected_obj.object_type == ObjectType.RECORD:
            self._obj_data_type.hide()
            self._obj_access_type.hide()
            self._obj_pdo_mapping.hide()
            self._obj_default_value.hide()
            self._obj_low_limit.hide()
            self._obj_high_limit.hide()
        else:
            if subindex == 0:
                self._obj_default_value.set_sensitive(False)
            else:
                self._obj_default_value.set_sensitive(True)
            self._obj_data_type.show()
            self._obj_access_type.show()
            self._obj_pdo_mapping.show()
            self._obj_default_value.show()
            self._obj_low_limit.show()
            self._obj_high_limit.show()
            if self._selected_obj.data_type in [DataType.VISIBLE_STRING, DataType.OCTET_STRING,
                                                DataType.UNICODE_STRING]:
                self._obj_default_value_len_label.show()

        self._obj_parameter_name.set_text(self._selected_obj.parameter_name)
        self._obj_denotation.set_text(self._selected_obj.denotation)
        obj_type = self._selected_obj.object_type
        self._obj_type.set_selected(list(ObjectType).index(obj_type))
        self._obj_comment.set_text(self._selected_obj.comments)
        storage_loc = self._selected_obj.storage_location
        if storage_loc:
            self._obj_storage_loc.set_selected(self._eds.storage_locations.index(storage_loc))
        if self._selected_obj.object_type == ObjectType.VAR:
            data_type = self._selected_obj.data_type
            self._obj_data_type.set_selected(list(DataType).index(data_type))
            access_type = self._selected_obj.access_type
            self._obj_access_type.set_selected(list(AccessType).index(access_type))
            self._obj_default_value.set_text(self._selected_obj.default_value)
            self._obj_pdo_mapping.set_active(self._selected_obj.pdo_mapping)
            self._obj_low_limit.set_text(self._selected_obj.low_limit)
            self._obj_high_limit.set_text(self._selected_obj.high_limit)
        elif self._selected_obj.object_type == ObjectType.ARRAY:
            if len(self._selected_obj) > 1:
                data_type = self._selected_obj[1].data_type
                self._obj_data_type.set_selected(list(DataType).index(data_type))
            else:  # array is empty, use dafault
                self._obj_data_type.set_selected(0)

    def _on_parametere_name_changed(self, entry: Gtk.Entry):
        if self._selected_obj:
            name = entry.get_text()
            self._selected_obj.parameter_name = name
            if self._parameter_name_cb:
                self._parameter_name_cb(name)

    def _on_obj_denotation_changed(self, entry: Gtk.Entry):
        if self._selected_obj:
            self._selected_obj.denotation = entry.get_text()

    def _on_obj_access_type_changed(self, dropdown: Gtk.DropDown, flag: Gtk.StateFlags):
        access_type = list(AccessType)[dropdown.get_selected()]
        if self._selected_obj:
            self._selected_obj.access_type = access_type

    def _on_obj_comment_changed(self, buffer: Gtk.TextBuffer):
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
        if self._selected_obj:
            self._selected_obj.comments = text

    def _on_obj_data_type_changed(self, dropdown: Gtk.DropDown, flag: Gtk.StateFlags):
        data_type = list(DataType)[dropdown.get_selected()]
        if self._selected_obj:
            self._selected_obj.data_type = data_type
            if self._selected_obj.data_type in [DataType.VISIBLE_STRING, DataType.OCTET_STRING,
                                                DataType.UNICODE_STRING]:
                self._obj_default_value_len_label.show()
            else:
                self._obj_default_value_len_label.hide()

    def _on_obj_pdo_mapping_changed(self, switch: Gtk.Switch, state: bool):
        if self._selected_obj:
            self._selected_obj.pdo_mapping = state

    def _on_obj_default_value_changed(self, entry: Gtk.Entry):
        text = entry.get_text()
        if self._selected_obj:
            self._selected_obj.default_value = text
            length = 0
            if self._selected_obj.data_type in [DataType.VISIBLE_STRING, DataType.UNICODE_STRING]:
                length = len(text)
            elif self._selected_obj.data_type == DataType.OCTET_STRING:
                length = m.ceil(len(text.replace(' ', '')) / 2)
            self._obj_default_value_len_label.set_text(f'(Length: {length})')

    def _on_obj_low_limit_changed(self, entry: Gtk.Entry):
        text = entry.get_text()
        if self._selected_obj:
            self._selected_obj.low_limit = text

    def _on_obj_high_limit_changed(self, entry: Gtk.Entry):
        text = entry.get_text()
        if self._selected_obj:
            self._selected_obj.high_limit = text

    def _on_obj_storage_loc_changed(self, dropdown: Gtk.DropDown, flag: Gtk.StateFlags):
        if self._eds.storage_locations:
            storage_location = self._eds.storage_locations[dropdown.get_selected()]
            if self._selected_obj:
                self._selected_obj.storage_location = storage_location
