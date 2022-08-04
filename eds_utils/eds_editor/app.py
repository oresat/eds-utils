from gi.repository import Gtk

from .window import AppWindow


class App(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.win = None
        self.file_path = None

        self.connect('activate', self.on_activate)

    def open_file(self, file_path: str):
        self.file_path = file_path

    def on_activate(self, app):
        self.win = AppWindow(application=app, title='EDS Editor')
        if self.file_path:
            self.win.open_file(self.file_path)
        self.win.present()
