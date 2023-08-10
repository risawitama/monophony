import monophony.backend.history
import monophony.backend.playlists
from monophony.frontend.rows.local_group_row import MonophonyLocalGroupRow
from monophony.frontend.rows.external_group_row import MonophonyExternalGroupRow
from monophony.frontend.rows.song_row import MonophonySongRow
from monophony.frontend.widgets.progress_bar import MonophonyProgressBar

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, GLib, Gtk


class MonophonyLibraryPage(Gtk.Box):
	def __init__(self, player: object):
		super().__init__(orientation=Gtk.Orientation.VERTICAL)

		self.player = player
		self.playlist_widgets = []
		self.recents_widgets = []
		self.old_recents = []
		self.set_vexpand(True)

		self.box_meta = Adw.PreferencesPage.new()
		self.box_meta.set_vexpand(True)
		self.box_meta.set_visible(False)
		self.box_meta.set_valign(Gtk.Align.FILL)
		self.append(self.box_meta)

		self.pge_status = Adw.StatusPage()
		self.pge_status.set_vexpand(True)
		self.pge_status.set_visible(False)
		self.pge_status.set_valign(Gtk.Align.FILL)
		self.pge_status.set_icon_name('io.gitlab.zehkira.Monophony')
		self.pge_status.set_title(_('Your Library is Empty'))
		self.pge_status.set_description(
			_('Find songs to play using the search bar above')
		)
		self.append(self.pge_status)

		bar_loading = MonophonyProgressBar(_('Loading Library...'))
		bar_loading.set_halign(Gtk.Align.CENTER)
		bar_loading.set_valign(Gtk.Align.CENTER)
		bar_loading.set_vexpand(True)
		self.box_loading = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.box_loading.set_margin_bottom(10)
		self.box_loading.append(bar_loading)
		self.append(self.box_loading)
		self.box_loading.set_visible(True)

		self.btn_play = Gtk.Button.new_with_label(_('Play All'))
		self.btn_play.connect('clicked', self._on_play_all)
		self.box_playlists = Adw.PreferencesGroup()
		self.box_playlists.set_title(_('Your Playlists'))
		self.box_playlists.set_header_suffix(self.btn_play)
		self.box_meta.add(self.box_playlists)

		self.box_recents = Adw.PreferencesGroup()
		self.box_recents.set_visible(False)
		self.box_recents.set_title(_('Recently Played'))
		self.box_meta.add(self.box_recents)

		GLib.Thread.new(
			None, monophony.backend.playlists.update_external_playlists, bar_loading
		)
		GLib.timeout_add(100, self.update)

	def _on_play_all(self, _b):
		all_songs = []
		for _title, content in monophony.backend.playlists.read_playlists().items():
			all_songs.extend(content)
		for playlist in monophony.backend.playlists.read_external_playlists():
			all_songs.extend(playlist['content'])

		GLib.Thread.new(None, self.player.play_queue, all_songs, 0)

	def update(self) -> bool:
		if not self.box_loading.get_last_child().lock.trylock():
			return True
		self.box_loading.get_last_child().lock.unlock()
		self.box_loading.set_visible(False)

		new_playlists = monophony.backend.playlists.read_playlists()
		new_ext_lists = monophony.backend.playlists.read_external_playlists()

		remaining_widgets = []
		for widget in self.playlist_widgets:
			if widget.is_ancestor(self.box_meta):
				remaining_widgets.append(widget)
		self.playlist_widgets = remaining_widgets

		for title in new_playlists.keys():
			for widget in self.playlist_widgets:
				if widget.get_title() == GLib.markup_escape_text(title, -1):
					break
			else: # nobreak
				new_widget = MonophonyLocalGroupRow(
					{'title': title, 'contents': new_playlists[title]}, self.player
				)
				self.playlist_widgets.append(new_widget)
				self.box_playlists.add(new_widget)

		for playlist in new_ext_lists:
			title = GLib.markup_escape_text(playlist['title'], -1)
			for widget in self.playlist_widgets:
				if widget.get_title() == title:
					break
			else: # nobreak
				new_widget = MonophonyExternalGroupRow(playlist, self.player)
				self.playlist_widgets.append(new_widget)
				self.box_playlists.add(new_widget)

		self.box_playlists.set_visible(len(self.playlist_widgets) > 0)

		# player could be adding to recents at this moment
		if self.player.is_busy():
			return True

		new_recents = monophony.backend.history.read_songs()
		new_recents.reverse()
		if new_recents != self.old_recents:
			self.box_recents.set_visible(True)

			for widget in self.recents_widgets:
				self.box_recents.remove(widget)

			self.recents_widgets = []
			self.old_recents = new_recents
			for song in new_recents:
				widget = MonophonySongRow(song, self.player)
				self.box_recents.add(widget)
				self.recents_widgets.append(widget)

		self.box_meta.set_visible(
			self.box_playlists.get_visible() or self.box_recents.get_visible()
		)
		self.pge_status.set_visible(
			not (self.box_meta.get_visible() or self.box_loading.get_visible())
		)
		return True
