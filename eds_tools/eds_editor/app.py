from gi.repository import GLib, Gio, Gtk

from .window import AppWindow

MENU_XML = '''
<?xml version='1.0' encoding='UTF-8'?>
<interface>
  <menu id='app-menu'>
    <section>
      <item>
        <attribute name='action'>app.new</attribute>
        <attribute name='label' translatable='yes'>New</attribute>
        <attribute name='accel'>&lt;Primary&gt;n</attribute>
      </item>
      <item>
        <attribute name='action'>app.open</attribute>
        <attribute name='label' translatable='yes'>Open</attribute>
        <attribute name='accel'>&lt;Primary&gt;o</attribute>
      </item>
      <item>
        <attribute name='action'>app.save</attribute>
        <attribute name='label' translatable='yes'>Save</attribute>
        <attribute name='accel'>&lt;Primary&gt;s</attribute>
      </item>
      <item>
        <attribute name='action'>app.save_as</attribute>
        <attribute name='label' translatable='yes'>Save As</attribute>
      </item>
    </section>
    <section>
      <item>
        <attribute name='action'>app.about</attribute>
        <attribute name='label' translatable='yes'>_About</attribute>
      </item>
      <item>
        <attribute name='action'>app.quit</attribute>
        <attribute name='label' translatable='yes'>_Quit</attribute>
        <attribute name='accel'>&lt;Primary&gt;q</attribute>
    </item>
    </section>
  </menu>
</interface>
'''


class App(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id='org.example.myapp',
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            **kwargs
        )
        self.window = None
        self.file_path = None

        self.add_main_option(
            'test',
            ord('t'),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            'Command line test',
            None,
        )

    def open_file(self, file_path: str):
        self.file_path = file_path

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new('new', None)
        action.connect('activate', self.on_new)
        self.add_action(action)

        action = Gio.SimpleAction.new('open', None)
        action.connect('activate', self.on_open)
        self.add_action(action)

        action = Gio.SimpleAction.new('save', None)
        action.connect('activate', self.on_save)
        self.add_action(action)

        action = Gio.SimpleAction.new('save_as', None)
        action.connect('activate', self.on_save_as)
        self.add_action(action)

        action = Gio.SimpleAction.new('about', None)
        action.connect('activate', self.on_about)
        self.add_action(action)

        action = Gio.SimpleAction.new('quit', None)
        action.connect('activate', self.on_quit)
        self.add_action(action)

        builder = Gtk.Builder.new_from_string(MENU_XML, -1)
        self.set_app_menu(builder.get_object('app-menu'))

    def do_activate(self):
        if not self.window:
            self.window = AppWindow(application=self, title='Main Window')
            self.window.show_all()
            if self.file_path:
                self.window.open_file(self.file_path)
        self.window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        # convert GVariantDict -> GVariant -> dict
        options = options.end().unpack()

        if 'test' in options:
            # This is printed on the main instance
            print('Test argument recieved: %s' % options['test'])

        self.activate()
        return 0

    def on_new(self, action, param):
        pass

    def on_open(self, action, param):
        dialog = Gtk.FileChooserDialog(
            'Please choose a file',
            self.window,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            file_path = dialog.get_filename()
            print('Open clicked')
            self.window.open_file(file_path)
            print('File selected: ' + file_path)
        elif response == Gtk.ResponseType.CANCEL:
            print('Cancel clicked')

        dialog.destroy()

    def on_save(self, action, param):
        self.window.save()

    def on_save_as(self, action, param):
        dialog = Gtk.FileChooserDialog(
            'Please choose a file',
            self.window,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            file_path = dialog.get_filename()
            print('Save clicked')
            print('File selected: ' + file_path)
        elif response == Gtk.ResponseType.CANCEL:
            print('Cancel clicked')

        dialog.destroy()

        self.window.save(file_path)

    def on_about(self, action, param):
        dialog = Gtk.AboutDialog(transient_for=self.window, modal=True)
        dialog.run()
        dialog.destroy()

    def on_quit(self, action, param):
        self.quit()
