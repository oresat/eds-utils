from gi.repository import Gtk

from .eds_notebook import EDSNotebook


class AppWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.stack = Gtk.Stack.new()
        self.set_child(self.stack)

        self.header = Gtk.HeaderBar()
        stack_switcher = Gtk.StackSwitcher().new()
        stack_switcher.set_stack(self.stack)
        self.header.set_title_widget(stack_switcher)
        self.set_titlebar(self.header)

        f = Gtk.FileFilter()
        f.set_name('CANopen files')
        f.add_pattern('*.dcf')
        f.add_pattern('*.eds')

        button = Gtk.Button(label='Open')
        button.set_icon_name('document-open-symbolic')
        button.set_tooltip_text('Open a project')
        button.connect('clicked', self.show_open_dialog)
        self.open_dialog = Gtk.FileChooserNative.new(title='Choose a file', parent=self,
                                                     action=Gtk.FileChooserAction.OPEN)
        self.open_dialog.connect('response', self.open_response)
        self.open_dialog.add_filter(f)
        self.header.pack_start(button)

        button = Gtk.Button(label='New')
        button.set_icon_name('document-new-symbolic')
        button.set_tooltip_text('Create a new project')
        button.connect('clicked', self.show_new_dialog)
        self.header.pack_start(button)

        button = Gtk.Button(label='Close')
        button.set_icon_name('edit-clear-symbolic')
        button.set_tooltip_text('Close the project')
        button.connect('clicked', self.on_click_close)
        self.header.pack_end(button)

        button = Gtk.Button(label='Save As')
        button.set_icon_name('document-save-as-symbolic')
        button.set_tooltip_text('Save the current project as a different name')
        button.connect('clicked', self.show_save_as_dialog)
        self.save_as_dialog = Gtk.FileChooserNative.new(title='Choose a file', parent=self,
                                                        action=Gtk.FileChooserAction.SAVE)
        self.save_as_dialog.connect('response', self.save_as_response)
        self.save_as_dialog.add_filter(f)
        self.header.pack_end(button)

        button = Gtk.Button(label='Save')
        button.set_icon_name('document-save-symbolic')
        button.set_tooltip_text('Save the project')
        button.connect('clicked', self.on_click_save)
        self.header.pack_end(button)

    def show_new_dialog(self, button):
        print('new TODO')

    def show_open_dialog(self, button):
        self.open_dialog.show()

    def open_eds(self, file_path: str):
        eds_notebook = EDSNotebook(file_path, self)
        self.stack.add_titled(eds_notebook, None, eds_notebook.eds_file)

    def open_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            file_path = file.get_path()
            self.open_eds(file_path)

    def on_click_save(self, button):
        eds_notebook = self.stack.get_visible_child()
        if eds_notebook:
            eds_notebook.save_eds()

    def show_save_as_dialog(self, button):
        self.save_as_dialog.show()

    def save_as_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            eds_notebook = self.stack.get_visible_child()
            if eds_notebook:
                file = dialog.get_file()
                file_path = file.get_path()
                eds_notebook.save_eds(file_path)

    def on_click_close(self, button):
        child = self.stack.get_visible_child()
        self.stack.remove(child)

        pages = self.stack.get_pages()
        if pages:
            child = pages[0].get_child()
            self.stack.set_visible_child(child)
