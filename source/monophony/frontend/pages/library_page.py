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

		self.btn_play = Gtk.Button.new_with_label(_('Play all'))
		self.btn_play.connect('clicked', self._on_play_all)
		self.box_playlists = Adw.PreferencesGroup()
		self.box_playlists.set_title(_('Playlists'))
		self.box_playlists.set_header_suffix(self.btn_play)
		self.add(self.box_playlists)

		GLib.timeout_add(100, self.update)

	def _on_play_all(self, _b):
		playlists = monophony.backend.playlists.read_playlists()
		all_songs = []
		for title, content in playlists.items():
			all_songs.extend(content)

		GLib.Thread.new(None, self.player.play_queue, all_songs, 0)

	def update(self) -> True:
		new_playlists = monophony.backend.playlists.read_playlists()

		if self.player.is_busy():
			self.btn_play.set_sensitive(False)
		else:
			self.btn_play.set_sensitive(True)

		remaining_widgets = []
		for widget in self.playlist_widgets:
			if widget.is_ancestor(self):
				remaining_widgets.append(widget)
		self.playlist_widgets = remaining_widgets

		for title in new_playlists.keys():
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

		if self.playlist_widgets:
			self.box_playlists.show()
		else:
			self.box_playlists.hide()

		return True
