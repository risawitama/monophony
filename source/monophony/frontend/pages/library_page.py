import monophony.backend.playlists
from monophony.frontend.widgets.group_row import MonophonyGroupRow
from monophony.frontend.widgets.song_row import MonophonySongRow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, GLib, Gtk


class MonophonyLibraryPage(Adw.PreferencesPage):
	def __init__(self, player: object):
		super().__init__()

		self.player = player
		self.playlist_widgets = []
		self.box_playlists = Adw.PreferencesGroup()
		self.box_playlists.set_title(_('Playlists'))
		self.add(self.box_playlists)
		GLib.timeout_add(100, self.update)

	def update(self) -> True:
		new_playlists = monophony.backend.playlists.read_playlists()
		new_titles = new_playlists.keys()

		kept_widgets = []
		for widget in self.playlist_widgets:
			if widget.get_title() not in new_titles:
				self.remove(widget) # XXX or will they remove themselves??
			else:
				kept_widgets.append(widget)
		self.playlist_widgets = kept_widgets

		for title in new_titles:
			for widget in self.playlist_widgets:
				if widget.get_title() == title:
					break
			else: # nobreak
				new_widget = MonophonyGroupRow(
					{'title': title, 'contents': new_playlists[title]},
					self.player,
					True
				)
				self.playlist_widgets.append(new_widget)
				self.box_playlists.add(new_widget)

		return True
