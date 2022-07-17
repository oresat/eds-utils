from os.path import abspath, dirname

from gi.repository import Gtk

from ..core import DataType, ObjectType, ACCESS_TYPE
from ..core.eds import EDS


class ObjectDictionaryPage:
    def __init__(self):
        self.eds = None

        builder = Gtk.Builder()

        path = dirname(abspath(__file__))
        builder.add_from_file(path + '/xml/object_dictionary_page.glade')
        self.page = builder.get_object('od_page')

        self.selected_obj = None

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

        update_button = builder.get_object('update_obj_button')
        update_button.connect('clicked', self.on_update_button_clicked)

        cancel_button = builder.get_object('cancel_obj_button')
        cancel_button.connect('clicked', self.on_cancel_button_clicked)

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
