from gi.repository import Gtk

from ..core import DataType, ObjectType, ACCESS_TYPE

from ..core.eds import EDS
from ..core.eds_format import VAR


class ObjectDictionaryPage(Gtk.ScrolledWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        box = Gtk.Box(homogeneous=True)
        self.set_child(box)

        box_tree = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5,
                           margin_top=5, margin_bottom=5,
                           margin_start=5, margin_end=5)
        box.append(box_tree)

        box_search = Gtk.Box(spacing=5)
        box_tree.append(box_search)

        self.search_filter_text = ''
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_hexpand(True)
        self.search_entry.connect('changed', self.on_search_entry)
        box_search.append(self.search_entry)

        button = Gtk.Button(label='Expand All')
        button.connect('clicked', self.on_expand_clicked)
        box_search.append(button)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_has_frame(True)
        box_tree.append(scrolled_window)

        self.indexes_store = Gtk.TreeStore(str, str)
        self.tree_filter = self.indexes_store.filter_new()
        self.tree_filter.set_visible_func(self.tree_filter_func)
        self.od_treeview = Gtk.TreeView(model=self.tree_filter)
        self.od_treeview.set_enable_tree_lines(True)
        for i, column_title in enumerate(['Object', 'Parameter Name']):
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
        self.obj_parameter_name.set_max_length(VAR['ParameterName'].max_length)
        grid.attach(label, column=0, row=0, width=1, height=1)
        grid.attach(self.obj_parameter_name, column=1, row=0, width=3, height=1)

        label = Gtk.Label.new('Object Type:')
        label.set_halign(Gtk.Align.START)
        self.obj_type = Gtk.DropDown()
        self.obj_type.set_sensitive(False)
        obj_type_list = Gtk.StringList.new(strings=[i.name for i in ObjectType])
        self.obj_type.set_model(obj_type_list)
        self.obj_type.set_selected(0)
        grid.attach(label, column=0, row=1, width=1, height=1)
        grid.attach(self.obj_type, column=1, row=1, width=1, height=1)

        label = Gtk.Label.new('Access Type:')
        label.set_halign(Gtk.Align.START)
        self.obj_access_type = Gtk.DropDown()
        access_type_list = Gtk.StringList.new(strings=ACCESS_TYPE)
        self.obj_access_type.set_model(access_type_list)
        self.obj_access_type.set_selected(0)
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
        grid.attach(label, column=0, row=2, width=1, height=5)
        grid.attach(scrolled_window, column=1, row=2, width=3, height=5)

        label = Gtk.Label.new('Data Type:')
        label.set_halign(Gtk.Align.START)
        self.obj_data_type = Gtk.DropDown()
        data_type_list = Gtk.StringList.new(strings=[i.name for i in DataType])
        self.obj_data_type.set_model(data_type_list)
        self.obj_data_type.set_selected(0)
        grid.attach(label, column=0, row=7, width=1, height=1)
        grid.attach(self.obj_data_type, column=1, row=7, width=1, height=1)

        label = Gtk.Label.new('PDO Mapping:')
        label.set_halign(Gtk.Align.START)
        self.obj_pdo_mapping = Gtk.Switch()
        self.obj_pdo_mapping.set_halign(Gtk.Align.START)
        self.obj_pdo_mapping.set_valign(Gtk.Align.CENTER)
        grid.attach(label, column=2, row=7, width=1, height=1)
        grid.attach(self.obj_pdo_mapping, column=3, row=7, width=1, height=1)

        label = Gtk.Label.new('Default Value:')
        label.set_halign(Gtk.Align.START)
        self.obj_default_value = Gtk.Entry()
        grid.attach(label, column=0, row=8, width=1, height=1)
        grid.attach(self.obj_default_value, column=1, row=8, width=3, height=1)

        button = Gtk.Button(label='Update')
        button.set_halign(Gtk.Align.END)
        button.set_valign(Gtk.Align.END)
        button.connect('clicked', self.on_update_button_clicked)
        grid.attach(button, column=0, row=9, width=2, height=2)

        button = Gtk.Button(label='Cancel')
        button.set_halign(Gtk.Align.START)
        button.set_valign(Gtk.Align.END)
        button.connect('clicked', self.on_cancel_button_clicked)
        grid.attach(button, column=2, row=9, width=2, height=2)

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

    def on_search_entry(self, entry) -> None:
        '''Callback on search filter entry for parameter names'''

        self.search_filter_text = self.search_entry.get_text().lower()
        self.tree_filter.refilter()

    def tree_filter_func(self, model, iter, data) -> bool:
        '''Callback on refilter to change row visibility

        Return
        ------
        bool
            True to show row,False to not show
        '''

        if self.search_filter_text:
            # check parent row's children rows for match
            for i in range(model.iter_n_children(iter)):
                subindex_iter = model.iter_nth_child(iter, i)
                if self.search_filter_text in model[subindex_iter][1].lower():
                    return True  # a subindex row contains search string

            return self.search_filter_text in model[iter][1].lower()

        return True  # no filter (show all)

    def on_expand_clicked(self, button) -> None:
        '''Callback on expand/collapse all button'''

        if button.get_label() == 'Expand All':
            self.od_treeview.expand_all()
            button.set_label('Collapse All')
        else:
            self.od_treeview.collapse_all()
            button.set_label('Expand All')

    def _loaf_selection(self):

        if self.selected_obj is None:
            return

        self.obj_parameter_name.set_text(self.selected_obj['ParameterName'])
        obj_type = self.selected_obj['ObjectType']
        self.obj_type.set_selected(list(ObjectType).index(obj_type))
        self.obj_comment.get_buffer().set_text(self.selected_obj.comment)
        if obj_type == ObjectType.VAR:
            data_type = self.selected_obj['DataType']
            self.obj_data_type.set_selected(list(DataType).index(data_type))
            access_type = self.selected_obj['AccessType']
            self.obj_access_type.set_selected(ACCESS_TYPE.index(access_type))
            self.obj_default_value.set_text(self.selected_obj['DefaultValue'])
            self.obj_pdo_mapping.set_state(self.selected_obj['PDOMapping'])
        else:
            self.obj_data_type.set_selected(0)
            self.obj_access_type.set_selected(0)
            self.obj_default_value.set_text('')
            self.obj_pdo_mapping.set_state(False)

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()

        if not treeiter:
            return

        if model[treeiter].parent is None:  # index
            index = model[treeiter][0]
            self.selected_obj = self.eds.index(index)
        else:  # subindex
            index = model[treeiter].parent[0]
            subindex = model[treeiter][0]
            self.selected_obj = self.eds.subindex(index, subindex)

        self._loaf_selection()

    def load_eds(self, eds: EDS):
        self.eds = eds

        for index in self.eds.indexes():
            index_section = self.eds.index(index)
            self.indexes_store.append(None, [index, index_section['ParameterName']])
            if index_section['ObjectType'] != ObjectType.VAR:
                for subindex in self.eds.subindexes(index):
                    subindex_section = self.eds.subindex(index, subindex)
                    self.indexes_store.append(self.indexes_store[-1].iter,
                                              [subindex, subindex_section['ParameterName']])
