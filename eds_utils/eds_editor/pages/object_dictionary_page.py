from copy import deepcopy

from gi.repository import Gtk

from ...core import DataType, ObjectType, AccessType, StorageLocation, str2int
from ...core.eds import EDS
from ...core.objects import Variable, Array, Record
from ..dialogs.errors_dialog import ErrorsDialog
from ..dialogs.add_object_dialog import AddObjectDialog
from ..dialogs.copy_object_dialog import CopyObjectDialog
from .page import Page


class ObjectDictionaryPage(Page):
    '''A page to edit the object dictionary of the eds / dcf file.'''

    def __init__(self, eds: EDS, parent_window: Gtk.Window):
        super().__init__(eds)

        self._parent_window = parent_window

        self._selected_obj = None
        self._selected_index = None
        self._selected_subindex = None

        box = Gtk.Box()
        self.set_child(box)

        box_tree = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5,
                           margin_top=5, margin_bottom=5,
                           margin_start=5, margin_end=5)
        box.append(box_tree)

        box_search = Gtk.Box(spacing=5)
        box_tree.append(box_search)

        self._search_filter_text = ''
        self._search_entry = Gtk.SearchEntry()
        self._search_entry.set_hexpand(True)
        self._search_entry.connect('changed', self.on_search_entry)
        box_search.append(self._search_entry)

        button = Gtk.Button(label='Expand All')
        button.connect('clicked', self.on_expand_clicked)
        box_search.append(button)

        self._od_scrolled_window = Gtk.ScrolledWindow()
        self._od_scrolled_window.set_vexpand(True)
        self._od_scrolled_window.set_hexpand(True)
        self._od_scrolled_window.set_has_frame(True)
        box_tree.append(self._od_scrolled_window)

        self._indexes_store = Gtk.TreeStore(str, str)
        self._tree_filter = self._indexes_store.filter_new()
        self._tree_filter.set_visible_func(self.tree_filter_func)
        self._od_treeview = Gtk.TreeView()
        self._od_scrolled_window.set_child(self._od_treeview)
        self._od_treeview.set_model(self._tree_filter)
        self._od_treeview.set_enable_tree_lines(True)

        for i, column_title in enumerate(['Object', 'Parameter Name']):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self._od_treeview.append_column(column)

        select = self._od_treeview.get_selection()
        select.connect('changed', self.on_tree_selection_changed)

        box_button = Gtk.Box()
        box_button.set_halign(Gtk.Align.CENTER)
        box_tree.append(box_button)

        button = Gtk.Button(label='Add')
        button.connect('clicked', self.add_treeview_object_on_click)
        box_button.append(button)

        button = Gtk.Button(label='Remove')
        button.connect('clicked', self.remove_treeview_object_on_click)
        box_button.append(button)

        button = Gtk.Button(label='Move')
        button.connect('clicked', self.move_object_on_click)
        box_button.append(button)

        button = Gtk.Button(label='Copy')
        button.connect('clicked', self.copy_object_on_click)
        box_button.append(button)

        frame = Gtk.Frame(label='Selected Object', margin_top=5, margin_bottom=5,
                          margin_start=5, margin_end=5)
        frame.set_valign(Gtk.Align.START)
        box.append(frame)

        grid = Gtk.Grid(column_spacing=5, row_spacing=5,
                        column_homogeneous=True, row_homogeneous=True,
                        margin_top=5, margin_bottom=5, margin_start=5, margin_end=5)
        frame.set_valign(Gtk.Align.START)
        frame.set_child(grid)

        label = Gtk.Label.new('Parameter Name:')
        label.set_halign(Gtk.Align.START)
        self._obj_parameter_name = Gtk.Entry()
        self._obj_parameter_name.set_max_length(241)
        grid.attach(label, column=0, row=0, width=1, height=1)
        grid.attach(self._obj_parameter_name, column=1, row=0, width=3, height=1)

        label = Gtk.Label.new('Denotation (DCF only):')
        label.set_halign(Gtk.Align.START)
        self._obj_denotation = Gtk.Entry()
        self._obj_denotation.set_max_length(241)
        grid.attach(label, column=0, row=1, width=1, height=1)
        grid.attach(self._obj_denotation, column=1, row=1, width=3, height=1)

        label = Gtk.Label.new('Object Type:')
        label.set_halign(Gtk.Align.START)
        self._obj_type = Gtk.DropDown()
        self._obj_type.set_sensitive(False)
        obj_type_list = Gtk.StringList.new(strings=[i.name for i in ObjectType])
        self._obj_type.set_model(obj_type_list)
        self._obj_type.set_selected(0)
        grid.attach(label, column=0, row=2, width=1, height=1)
        grid.attach(self._obj_type, column=1, row=2, width=1, height=1)

        label = Gtk.Label.new('Access Type:')
        label.set_halign(Gtk.Align.START)
        self._obj_access_type = Gtk.DropDown()
        access_type_list = Gtk.StringList.new(strings=[i.name for i in AccessType])
        self._obj_access_type.set_model(access_type_list)
        self._obj_access_type.set_selected(0)
        grid.attach(label, column=2, row=2, width=1, height=1)
        grid.attach(self._obj_access_type, column=3, row=2, width=1, height=1)

        label = Gtk.Label.new('Comment:')
        label.set_halign(Gtk.Align.START)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_has_frame(True)
        self._obj_comment = Gtk.TextView()
        scrolled_window.set_child(self._obj_comment)
        grid.attach(label, column=0, row=3, width=1, height=5)
        grid.attach(scrolled_window, column=1, row=3, width=3, height=5)

        label = Gtk.Label.new('Data Type:')
        label.set_halign(Gtk.Align.START)
        self._obj_data_type = Gtk.DropDown()
        data_type_list = Gtk.StringList.new(strings=[i.name for i in DataType])
        self._obj_data_type.set_model(data_type_list)
        self._obj_data_type.set_selected(0)
        grid.attach(label, column=0, row=8, width=1, height=1)
        grid.attach(self._obj_data_type, column=1, row=8, width=1, height=1)

        label = Gtk.Label.new('PDO Mapping:')
        label.set_halign(Gtk.Align.START)
        self._obj_pdo_mapping = Gtk.Switch()
        self._obj_pdo_mapping.set_halign(Gtk.Align.START)
        self._obj_pdo_mapping.set_valign(Gtk.Align.CENTER)
        grid.attach(label, column=2, row=8, width=1, height=1)
        grid.attach(self._obj_pdo_mapping, column=3, row=8, width=1, height=1)

        label = Gtk.Label.new('Default Value:')
        label.set_halign(Gtk.Align.START)
        self._obj_default_value = Gtk.Entry()
        grid.attach(label, column=0, row=9, width=1, height=1)
        grid.attach(self._obj_default_value, column=1, row=9, width=3, height=1)

        label = Gtk.Label.new('Low Limit:')
        label.set_halign(Gtk.Align.START)
        self._obj_low_limit = Gtk.Entry()
        grid.attach(label, column=0, row=10, width=1, height=1)
        grid.attach(self._obj_low_limit, column=1, row=10, width=1, height=1)

        label = Gtk.Label.new('High Limit:')
        label.set_halign(Gtk.Align.START)
        self._obj_high_limit = Gtk.Entry()
        grid.attach(label, column=2, row=10, width=1, height=1)
        grid.attach(self._obj_high_limit, column=3, row=10, width=1, height=1)

        label = Gtk.Label.new('Storage Location (CANopenNode):')
        label.set_halign(Gtk.Align.START)
        self._obj_storage_loc = Gtk.DropDown()
        storage_loc_list = Gtk.StringList.new(strings=[i.name for i in StorageLocation])
        self._obj_storage_loc.set_model(storage_loc_list)
        self._obj_storage_loc.set_selected(0)
        grid.attach(label, column=0, row=11, width=1, height=1)
        grid.attach(self._obj_storage_loc, column=1, row=11, width=1, height=1)

        button = Gtk.Button(label='Update')
        button.set_halign(Gtk.Align.END)
        button.set_valign(Gtk.Align.END)
        button.connect('clicked', self.on_update_button_clicked)
        grid.attach(button, column=0, row=12, width=2, height=2)

        button = Gtk.Button(label='Cancel')
        button.set_halign(Gtk.Align.START)
        button.set_valign(Gtk.Align.END)
        button.connect('clicked', self.on_cancel_button_clicked)
        grid.attach(button, column=2, row=12, width=2, height=2)

        self.reload_eds()

    def on_update_button_clicked(self, button: Gtk.Button):
        '''Update button callback to save changes the selected object.'''

        if self._selected_obj is None:
            return

        self._eds_changed = True

        self._selected_obj.parameter_name = self._obj_parameter_name.get_text()
        buf = self._obj_comment.get_buffer()
        self._selected_obj.comments = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False)
        data_type = self._obj_data_type.get_selected()
        self._selected_obj.data_type = list(DataType)[data_type]
        access_type = self._obj_access_type.get_selected()
        self._selected_obj.access_type = list(AccessType)[access_type]
        self._selected_obj.default_value = self._obj_default_value.get_text()
        self._selected_obj.pdo_mapping = self._obj_pdo_mapping.get_state()
        storage_loc = self._obj_storage_loc.get_selected()
        self._selected_obj.storage_location = list(StorageLocation)[storage_loc]

    def on_cancel_button_clicked(self, button: Gtk.Button):
        '''Cancel button callback to cancel changes the selected object.'''

        self._load_selection()

    def on_search_entry(self, entry):
        '''Callback on search filter entry for parameter names'''

        if self._tree_filter:
            self._search_filter_text = self._search_entry.get_text().lower()
            self._tree_filter.refilter()

    def tree_filter_func(self, model, iter, data) -> bool:
        '''Callback on refilter to change row visibility

        Return
        ------
        bool
            True to show row,False to not show
        '''

        if self._search_filter_text:
            # check parent row's children rows for match
            for i in range(model.iter_n_children(iter)):
                subindex_iter = model.iter_nth_child(iter, i)
                if self._search_filter_text in model[subindex_iter][1].lower():
                    return True  # a subindex row contains search string

            return self._search_filter_text in model[iter][1].lower()

        return True  # no filter (show all)

    def on_expand_clicked(self, button):
        '''Callback on expand/collapse all button'''

        if button.get_label() == 'Expand All':
            self._od_treeview.expand_all()
            button.set_label('Collapse All')
        else:
            self._od_treeview.collapse_all()
            button.set_label('Expand All')

    def _load_selection(self):
        '''Load the select object info'''

        if self._selected_obj is None:
            return

        self._obj_parameter_name.set_text(self._selected_obj.parameter_name)
        self._obj_denotation.set_text(self._selected_obj.denotation)
        obj_type = self._selected_obj.object_type
        self._obj_type.set_selected(list(ObjectType).index(obj_type))
        self._obj_comment.get_buffer().set_text(self._selected_obj.comments)
        storage_loc = self._selected_obj.storage_location
        self._obj_storage_loc.set_selected(list(StorageLocation).index(storage_loc))
        if self._selected_obj.object_type == ObjectType.VAR:
            data_type = self._selected_obj.data_type
            self._obj_data_type.set_selected(list(DataType).index(data_type))
            access_type = self._selected_obj.access_type
            self._obj_access_type.set_selected(list(AccessType).index(access_type))
            self._obj_default_value.set_text(self._selected_obj.default_value)
            self._obj_pdo_mapping.set_state(self._selected_obj.pdo_mapping)
            self._obj_low_limit.set_text(self._selected_obj.low_limit)
            self._obj_high_limit.set_text(self._selected_obj.high_limit)
        elif self._selected_obj.object_type == ObjectType.ARRAY:
            if len(self._selected_obj) > 1:
                data_type = self._selected_obj[1].data_type
                self._obj_data_type.set_selected(list(DataType).index(data_type))
            else:  # array is empty, use dafault
                self._obj_data_type.set_selected(0)

    def on_tree_selection_changed(self, selection: Gtk.SelectionModel):
        '''When value is selected in the treeview, change the current selected object.'''
        model, treeiter = selection.get_selected()

        if not treeiter:
            return  # no values in treeview

        # reset these
        self._obj_data_type.set_sensitive(True)
        self._obj_storage_loc.set_sensitive(True)
        self._obj_default_value.set_sensitive(True)

        if model[treeiter].parent is None:  # index
            index_str = model[treeiter][0]
            index = str2int(index_str)
            self._selected_obj = self._eds[index]
            self._selected_index = index
            self._selected_subindex = None
        else:  # subindex
            index_str = model[treeiter].parent[0]
            index = str2int(index_str)
            subindex_str = model[treeiter][0]
            subindex = str2int(subindex_str)
            self._selected_obj = self._eds[index][subindex]
            self._selected_index = index
            self._selected_subindex = subindex
            self._obj_storage_loc.set_sensitive(False)

            if subindex == 0:
                self._obj_data_type.set_sensitive(False)
                self._obj_default_value.set_sensitive(False)
            elif self._eds[index].object_type == ObjectType.ARRAY:
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
            self._obj_data_type.show()
            self._obj_access_type.show()
            self._obj_pdo_mapping.show()
            self._obj_default_value.show()
            self._obj_low_limit.show()
            self._obj_high_limit.show()

        self._load_selection()

    def reload_eds(self):
        '''Reload the eds in the treeview.'''
        self._indexes_store.clear()

        # fill tree view with object dictionary data
        for index in self._eds.indexes:
            index_str = f'0x{index:X}'
            index_section = self._eds[index]
            self._indexes_store.append(None, [index_str, index_section.parameter_name])
            if index_section.object_type != ObjectType.VAR:
                for subindex in self._eds[index].subindexes:
                    subindex_str = f'0x{subindex:X}'
                    subindex_section = self._eds[index][subindex]
                    self._indexes_store.append(self._indexes_store[-1].iter,
                                               [subindex_str, subindex_section.parameter_name])

    def add_treeview_obj(self, index: int, subindex: int, name: str):
        '''
        Add a new object to the treeview

        Parameters
        ----------
        index: int
            The index of the new object.
        subindex: int
            The subindex of the new object. If not a subindex set to a negative number.
        name: str
            The name of the new object.
        '''

        self._eds_changed = True
        index_str = f'0x{index:X}'

        index_found = False
        for i in self._indexes_store:
            if index == str2int(i[0]):
                if subindex < 0:
                    raise ValueError(f'index {index_str} already exists')

                for j in i.iterchildren():
                    subindex_str = f'0x{subindex:X}'
                    if subindex < 0:
                        msg = f'index {index_str} subindex {subindex_str} already exists'
                        raise ValueError(msg)

                    if subindex < str2int(j[0]):
                        # insert new object before subindex
                        new_iter = self._indexes_store.insert_before(None, j.iter)
                        self._indexes_store.set_value(new_iter, 0, subindex_str)
                        self._indexes_store.set_value(new_iter, 1, name)
                        index_found = True
                        break

                if not index_found:
                    # new subindex exceed all existing ones
                    subindex_str = f'0x{subindex:X}'
                    self._indexes_store.append(i.iter, [subindex_str, name])
                    index_found = True
                    break
                else:
                    # new index was found in subindex loop, break index loop
                    break
            elif index < str2int(i[0]):
                # insert new object before index
                new_iter = self._indexes_store.insert_before(None, i.iter)
                self._indexes_store.set_value(new_iter, 0, index_str)
                self._indexes_store.set_value(new_iter, 1, name)
                index_found = True
                break

        if not index_found:
            # new index exceed all existing ones
            self._indexes_store.append(None, [index_str, name])

    def remove_treeview_obj(self, index: int, subindex: int):
        '''
        Remove an object from the treeview.

        Parameters
        ----------
        index: int
            The index of the object to remove.
        subindex: int
            The subindex of the object to remove.
        '''

        self._eds_changed = True

        for i in self._indexes_store:
            if index == str2int(i[0]):
                if self._selected_subindex is None:  # remove index
                    self._indexes_store.remove(i.iter)
                    break
                else:  # remove subindex
                    for j in i.iterchildren():
                        if subindex == str2int(j[0]):
                            self._indexes_store.remove(j.iter)
                            break
                    break  # stop index loop

    def update_obj(self, index: int, subindex: int, name: str):
        '''
        Update an object in the treeview.

        Parameters
        ----------
        index: int
            The index of the object to update.
        subindex: int
            The subindex of the object to update.
        name: str
            The name of the new object.
        '''

        self._eds_changed = True

        for i in self._indexes_store:
            if index == str2int(i[0]):
                if self._selected_subindex is None:  # remove index
                    self._indexes_store.set_value(i.iter, 1, name)
                    break
                else:  # remove subindex
                    for j in i.iterchildren():
                        if subindex == str2int(j[0]):
                            self._indexes_store.set_value(j.iter, 1, name)
                            break
                    break  # stop index loop

    def add_treeview_object_on_click(self, button: Gtk.Button):
        '''Callback for the add object to OD button. Opens the add object dialog.'''

        dialog = AddObjectDialog(self._parent_window, self._eds)
        dialog.connect('response', self.add_treeview_object_response)
        dialog.show()

    def add_treeview_object_response(self, dialog: Gtk.Dialog, response: int):
        '''Parses the response to the ad object dialog..'''

        self._eds_changed = True

        new_index, new_subindex, new_obj_type = dialog.get_response()

        # add new object to eds
        if new_subindex is None:
            if new_obj_type == ObjectType.VAR:
                obj = Variable()
            elif new_obj_type == ObjectType.ARRAY:
                obj = Array()
            else:
                obj = Record()
            self._eds[new_index] = obj
        else:
            obj = Variable()
            if new_obj_type == ObjectType.ARRAY:
                # all data types in arrays must match
                obj.data_type = self._eds[new_index].data_type
            self._eds[new_index][new_subindex] = obj

        # add new object to treeview
        self.add_treeview_obj(new_index, new_subindex, obj.parameter_name)

        # add subindex0 for new arrays and records to treeview
        if new_obj_type in [ObjectType.ARRAY, ObjectType.RECORD]:
            self.add_treeview_obj(new_index, 0, obj[0].parameter_name)

    def check_selected(self) -> list:
        '''Check the select object is for move / copy / removal operations. If the object cannot be
        moved / copied / removed an errors dialog will be displayed.


        Returns
        -------
        list
            The list of errors messages. Will be an empty list for no errors.
        '''

        errors = []

        if self._selected_index in self._eds.MANDATORY_OBJECTS:
            errors.append(f'Cannot move/remove a mandotory object of 0x{self._selected_index:X}')

        if self._selected_subindex == 0:
            errors.append('Cannot move/remove subindex 0 of Arrays or Records')

        if errors:
            errors_dialog = ErrorsDialog(self._parent_window)
            errors_dialog.errors = errors
            errors_dialog.show()

        return errors

    def remove_treeview_object_on_click(self, button: Gtk.Button):
        '''Callback for the remove object to OD button.'''

        if self.check_selected():
            return  # invalid object to remove

        if self._selected_index not in self._eds.indexes:
            return  # nothing to delete

        self._eds_changed = True

        # remove from od
        if self._selected_subindex is None:
            del self._eds[self._selected_index]
        elif self._selected_subindex in self._eds[self._selected_index].subindexes:
            del self._eds[self._selected_index][self._selected_subindex]

        # remove from treeview
        self.remove_treeview_obj(self._selected_index, self._selected_subindex)

    def copy_object_on_click(self, button: Gtk.Button):
        '''Callback for the copy object to OD button. Opens the copy object dialog.'''

        dialog = CopyObjectDialog(self._parent_window, self._eds, self._selected_index,
                                  self._selected_subindex)
        dialog.connect('response', self.copy_treeview_object_response)
        dialog.show()

    def copy_treeview_object_response(self, dialog: Gtk.Dialog, response: int):
        '''Parses the response to the copy object dialog..'''

        self._eds_changed = True

        new_index, new_subindex = dialog.get_response()

        # add new object to eds
        if new_subindex is None and self._selected_subindex is None:
            # copy a index to a new index
            self._eds[new_index] = deepcopy(self._eds[self._selected_index])
        elif new_subindex is not None and self._selected_subindex is None:
            # copy a index to a new subindex
            self._eds[new_index][new_subindex] = deepcopy(self._eds[self._selected_index])
        elif new_subindex is None and self._selected_subindex is not None:
            # copy a subindex to a new index
            temp = deepcopy(self._eds[self._selected_index][self._selected_subindex])
            self._eds[new_index] = temp
        else:
            # copy a subindex to a new subindex
            temp = deepcopy(self._eds[self._selected_index][self._selected_subindex])
            self._eds[new_index][new_subindex] = temp

        # add new object to treeview
        name = self._selected_obj.parameter_name
        self.add_treeview_obj(new_index, new_subindex, name)

    def move_object_on_click(self, button: Gtk.Button):
        '''Callback for the move object to OD button. Opens the move object dialog.'''

        if self.check_selected():
            return  # invalid object to move

        dialog = CopyObjectDialog(self._parent_window, self._eds, self._selected_index,
                                  self._selected_subindex, move=True)
        dialog.connect('response', self.move_treeview_object_response)
        dialog.show()

    def move_treeview_object_response(self, dialog: Gtk.Dialog, response: int):
        '''Parses the response to the move object dialog..'''

        self._eds_changed = True

        new_index, new_subindex = dialog.get_response()

        # move object in eds
        if new_subindex is None and self._selected_subindex is None:
            # move a index to a new index
            self._eds[new_index] = deepcopy(self._eds[self._selected_index])
            del self._eds[self._selected_index]
        elif new_subindex is not None and self._selected_subindex is None:
            # move a index to a new subindex
            self._eds[new_index][new_subindex] = deepcopy(self._eds[self._selected_index])
            del self._eds[self._selected_index]
        elif new_subindex is None and self._selected_subindex is not None:
            # move a subindex to a new index
            self._eds[new_index] = \
                deepcopy(self._eds[self._selected_index][self._selected_subindex])
            del self._eds[self._selected_index][self._selected_subindex]
        else:
            # move a subindex to a new subindex
            temp = deepcopy(self._eds[self._selected_index][self._selected_subindex])
            self._eds[new_index][new_subindex] = temp
            del self._eds[self._selected_index][self._selected_subindex]

        # move object in treeview
        name = self._selected_obj.parameter_name
        self.add_treeview_obj(new_index, new_subindex, name)
        self.remove_treeview_obj(self._selected_index, self._selected_subindex)
