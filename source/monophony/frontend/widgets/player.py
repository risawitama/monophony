import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gtk


class MonophonyPlayer(Gtk.Box):
	def __init__(self):
		super().__init__(orientation = Gtk.Orientation.VERTICAL)
