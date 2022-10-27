from gi.repository import Gtk


class ErrorsDialog(Gtk.Dialog):
    '''Gtk Dialog to display all the erros when parsing an eds / dcf file.'''

    def __init__(self, parent: Gtk.Window):
        '''
        Parameter
        ---------
        parent: Gtk.Window
            The parent window to attach to.
        '''

        super().__init__(title='Errors', transient_for=parent)

        self.set_transient_for(parent)

        self.set_default_size(500, 500)

        box = self.get_content_area()

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        box.append(scrolled_window)

        self._errors_text = Gtk.Label()
        scrolled_window.set_child(self._errors_text)

        close_button = Gtk.Button.new_with_label(label='Close')
        close_button.connect('clicked', self.on_close_button_clicked)
        box.append(close_button)

    def on_close_button_clicked(self, button: Gtk.Button):
        '''On the close button clicked, close the dialog.'''

        self.destroy()

    @property
    def errors(self) -> list:
        '''list: The errors when parsing the eds / dcf file.'''

        return self._errors_text.get_text().split('\n')

    @errors.setter
    def errors(self, errors: list):

        self._errors_text.set_text('\n'.join(errors))
