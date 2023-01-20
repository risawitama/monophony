from monophony.frontend.widgets.group_row import MonophonyGroupRow
from monophony.frontend.widgets.song_row import MonophonySongRow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gtk


class MonophonySearchPage(Gtk.Box):
	def __init__(self):
		super().__init__(orientation = Gtk.Orientation.VERTICAL)

		self.set_vexpand(True)
		self.group_rows = []
