from gi.repository import Gtk


class ErrorsDialog(Gtk.Dialog):

    def __init__(self, parent):

        super().__init__(title='Errors', transient_for=parent)

        self.set_transient_for(parent)

        box = self.get_content_area()

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        box.append(scrolled_window)

        self._errors_text = Gtk.Label()
        scrolled_window.set_child(self._errors_text)

        close_button = Gtk.Button.new_with_label(label='Close')
        close_button.connect('clicked', self._close)
        box.append(close_button)

    def _close(self, button: Gtk.Button) -> None:

        self.destroy()

    @property
    def errors(self) -> list:

        return self._errors_text.get_text().split('\n')

    @errors.setter
    def errors(self, errors: list) -> None:

        self._errors_text.set_text('\n'.join(errors))
