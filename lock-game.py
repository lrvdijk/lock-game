from gi.repository import Gtk, GObject

from lockgame.window import MainWindow

if __name__ == '__main__':
    GObject.threads_init()

    window = MainWindow()
    window.connect('delete-event', Gtk.main_quit)
    window.show_all()

    Gtk.main()
