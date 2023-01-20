from monophony.frontend.widgets.group_row import MonophonyGroupRow
from monophony.frontend.widgets.song_row import MonophonySongRow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gtk


class MonophonyLibraryPage(Gtk.ScrolledWindow):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		box_recommendations = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		box_recommendations.set_valign(Gtk.Align.START)

		box_playlists = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		box_playlists.set_valign(Gtk.Align.START)

		box_library = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		box_library.set_spacing(20)
		box_library.set_margin_top(10)
		box_library.set_margin_bottom(10)
		box_library.append(box_recommendations)
		box_library.append(box_playlists)

		clamp = Adw.Clamp()
		clamp.set_child(box_library)

		self.group_rows = []
