from gi.repository import Gtk

from lockgame.window import MainWindow

if __name__ == '__main__':
    window = MainWindow()
    window.connect('delete-event', Gtk.main_quit)
    window.show_all()

    Gtk.main()
