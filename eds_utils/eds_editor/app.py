from gi.repository import Gtk

from .window import AppWindow


class App(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.win = None
        self.file_paths = []

        self.connect('activate', self.on_activate)

    def open_eds(self, file_path: str):
        self.file_paths.append(file_path)

    def on_activate(self, app):
        self.win = AppWindow(application=app, title='EDS Editor')
        for i in self.file_paths:
            self.win.open_eds(i)
        self.win.present()
