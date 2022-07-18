from gi.repository import Gtk

from ..core import DataType, ObjectType, ACCESS_TYPE

from ..core.eds import EDS


class ObjectDictionaryPage(Gtk.ScrolledWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        box = Gtk.Box(homogeneous=True)
        self.set_child(box)

        box_tree = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5,
                           margin_top=5, margin_bottom=5,
                           margin_start=5, margin_end=5)
        box.append(box_tree)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_has_frame(True)
        box_tree.append(scrolled_window)

        self.od_treeview = Gtk.TreeView()
        self.indexes_store = Gtk.TreeStore(str, str, str)
        self.od_treeview.set_model(self.indexes_store)
        for i, column_title in enumerate(['Index', 'Subindex', 'Parameter Name']):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.od_treeview.append_column(column)
        select = self.od_treeview.get_selection()
        select.connect('changed', self.on_tree_selection_changed)
        scrolled_window.set_child(self.od_treeview)

        box_button = Gtk.Box()
        box_button.set_halign(Gtk.Align.CENTER)
        box_tree.append(box_button)

        button = Gtk.Button(label='Add')
        box_button.append(button)

        button = Gtk.Button(label='Remove')
        box_button.append(button)

        button = Gtk.Button(label='Move')
        box_button.append(button)

        button = Gtk.Button(label='Copy')
        box_button.append(button)

        frame = Gtk.Frame(label='Selected Object', margin_top=5, margin_bottom=5,
                          margin_start=5, margin_end=5)
        frame.set_valign(Gtk.Align.START)

        box.append(frame)
        grid = Gtk.Grid(column_spacing=5, row_spacing=5,
                        column_homogeneous=True, row_homogeneous=True,
                        margin_top=5, margin_bottom=5, margin_start=5, margin_end=5)
        frame.set_child(grid)

        label = Gtk.Label.new('Parameter Name:')
        label.set_halign(Gtk.Align.START)
        self.obj_parameter_name = Gtk.Entry()
        grid.attach(label, column=0, row=0, width=1, height=1)
        grid.attach(self.obj_parameter_name, column=1, row=0, width=3, height=1)

        label = Gtk.Label.new('Object Type:')
        label.set_halign(Gtk.Align.START)
        self.obj_type = Gtk.ComboBox()
        self.obj_type.set_sensitive(False)
        liststore_type = Gtk.ListStore(str)
        for item in ObjectType:
            liststore_type.append([item.name])
        self.obj_type.set_model(liststore_type)
        self.obj_type.set_active(0)
        cellrenderertext = Gtk.CellRendererText()
        self.obj_type.pack_start(cellrenderertext, True)
        self.obj_type.add_attribute(cellrenderertext, 'text', 0)
        grid.attach(label, column=0, row=1, width=1, height=1)
        grid.attach(self.obj_type, column=1, row=1, width=1, height=1)

        label = Gtk.Label.new('Access Type:')
        label.set_halign(Gtk.Align.START)
        self.obj_access_type = Gtk.ComboBox()
        liststore_obj_data = Gtk.ListStore(str)
        for item in ACCESS_TYPE:
            liststore_obj_data.append([item])
        self.obj_access_type.set_model(liststore_obj_data)
        self.obj_access_type.set_active(0)
        cellrenderertext = Gtk.CellRendererText()
        self.obj_access_type.pack_start(cellrenderertext, True)
        self.obj_access_type.add_attribute(cellrenderertext, 'text', 0)
        grid.attach(label, column=2, row=1, width=1, height=1)
        grid.attach(self.obj_access_type, column=3, row=1, width=1, height=1)

        label = Gtk.Label.new('Comment:')
        label.set_halign(Gtk.Align.START)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_has_frame(True)
        self.obj_comment = Gtk.TextView()
        scrolled_window.set_child(self.obj_comment)
        grid.attach(label, column=0, row=2, width=1, height=3)
        grid.attach(scrolled_window, column=1, row=2, width=3, height=3)

        label = Gtk.Label.new('Data Type:')
        label.set_halign(Gtk.Align.START)
        self.obj_data_type = Gtk.ComboBox()
        liststore_obj_data = Gtk.ListStore(str)
        for item in DataType:
            liststore_obj_data.append([item.name])
        self.obj_data_type.set_model(liststore_obj_data)
        self.obj_data_type.set_active(0)
        cellrenderertext = Gtk.CellRendererText()
        self.obj_data_type.pack_start(cellrenderertext, True)
        self.obj_data_type.add_attribute(cellrenderertext, 'text', 0)
        grid.attach(label, column=0, row=5, width=1, height=1)
        grid.attach(self.obj_data_type, column=1, row=5, width=1, height=1)

        label = Gtk.Label.new('PDO Mapping:')
        label.set_halign(Gtk.Align.START)
        self.obj_pdo_mapping = Gtk.Switch()
        self.obj_pdo_mapping.set_halign(Gtk.Align.START)
        self.obj_pdo_mapping.set_valign(Gtk.Align.CENTER)
        grid.attach(label, column=2, row=5, width=1, height=1)
        grid.attach(self.obj_pdo_mapping, column=3, row=5, width=1, height=1)

        label = Gtk.Label.new('Default Value:')
        label.set_halign(Gtk.Align.START)
        self.obj_default_value = Gtk.Entry()
        grid.attach(label, column=0, row=6, width=1, height=1)
        grid.attach(self.obj_default_value, column=1, row=6, width=3, height=1)

        button = Gtk.Button(label='Update')
        button.set_halign(Gtk.Align.END)
        button.set_valign(Gtk.Align.END)
        button.connect('clicked', self.on_update_button_clicked)
        grid.attach(button, column=0, row=7, width=2, height=2)

        button = Gtk.Button(label='Cancel')
        button.set_halign(Gtk.Align.START)
        button.set_valign(Gtk.Align.END)
        button.connect('clicked', self.on_cancel_button_clicked)
        grid.attach(button, column=2, row=7, width=2, height=2)

    def on_update_button_clicked(self, button):

        if self.selected_obj is None:
            return

        self.selected_obj['ParameterName'] = self.obj_parameter_name.get_text()
        obj_type = self.obj_type.get_active()
        self.selected_obj['ObjectType'] = list(ObjectType)[obj_type]
        buf = self.obj_comment.get_buffer()
        self.selected_obj.comment = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False)
        data_type = self.obj_data_type.get_active()
        self.selected_obj['DataType'] = list(DataType)[data_type]
        access_type = self.obj_access_type.get_active()
        self.selected_obj['DataType'] = ACCESS_TYPE[access_type]
        self.selected_obj['DefaultValue'] = self.obj_default_value
        self.selected_obj['PDOMapping'] = self.obj_pdo_mapping

    def on_cancel_button_clicked(self, button):

        self._loaf_selection()

    def _loaf_selection(self):

        if self.selected_obj is None:
            return

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

        self._loaf_selection()

    def load_eds(self, eds: EDS):
        self.eds = eds

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