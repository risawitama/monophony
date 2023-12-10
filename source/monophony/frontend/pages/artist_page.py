import monophony.backend.yt
from monophony.frontend.rows.importable_group_row import MonophonyImportableGroupRow
from monophony.frontend.rows.locked_group_row import MonophonyLockedGroupRow
from monophony.frontend.widgets.big_spinner import MonophonyBigSpinner

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, GLib, Gtk


class MonophonyArtistPage(Gtk.Box):
	def __init__(self, player: object, artist: str):
		super().__init__(orientation=Gtk.Orientation.VERTICAL)

		self.pge_status = Adw.StatusPage()
		self.pge_status.set_vexpand(True)
		self.pge_status.set_valign(Gtk.Align.FILL)
		self.pge_status.set_icon_name('system-search-symbolic')
		self.pge_status.set_title(_('No Results'))
		self.pge_status.set_visible(False)
		self.append(self.pge_status)

		self.pge_results = Adw.PreferencesPage.new()
		self.pge_results.set_vexpand(True)
		self.pge_results.set_valign(Gtk.Align.FILL)
		self.pge_results.set_visible(False)
		self.append(self.pge_results)

		self.box_loading = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.box_loading.set_margin_bottom(10)
		self.box_loading.append(MonophonyBigSpinner())
		self.box_loading.set_visible(True)
		self.append(self.box_loading)

		self.set_vexpand(True)
		self.artist = artist
		self.results = []
		self.search_lock = GLib.Mutex()
		self.player = player

		GLib.Thread.new(None, self.do_get_artist)
		GLib.timeout_add(500, self.await_results)

	def do_get_artist(self):
		self.search_lock.lock()
		results = monophony.backend.yt.get_artist(self.artist)
		if not results:
			self.pge_status.set_title(_('Artist Not Found'))
			self.box_loading.set_visible(False)
			self.pge_status.set_visible(True)
			self.search_lock.unlock()
			return

		self.results = results
		self.search_lock.unlock()

	def await_results(self) -> bool:
		if not self.search_lock.trylock():
			return True

		self.box_loading.set_visible(False)
		self.pge_status.set_visible(len(self.results) == 0)
		if self.results:
			self.pge_results.set_visible(True)
			box_other = Adw.PreferencesGroup.new()
			box_albums = Adw.PreferencesGroup.new()
			box_playlists = Adw.PreferencesGroup.new()
			box_other.set_title(_('Other'))
			box_albums.set_title(_('Albums'))
			box_playlists.set_title(_('Community Playlists'))

			songs = []
			videos = []
			non_empty = []
			for item in self.results:
				if item['type'] == 'song':
					songs.append(item)
				elif item['type'] == 'video':
					videos.append(item)
				elif item['type'] == 'album':
					box_albums.add(MonophonyImportableGroupRow(item, self.player))
					if box_albums not in non_empty:
						non_empty.append(box_albums)
				elif item['type'] == 'playlist':
					box_playlists.add(MonophonyImportableGroupRow(item, self.player))
					if box_playlists not in non_empty:
						non_empty.append(box_playlists)
			if songs or videos:
				non_empty.append(box_other)
				if songs:
					box_other.add(
						MonophonyLockedGroupRow(
							{'title': _('All Songs'), 'contents': songs}, self.player
						)
					)
				if videos:
					box_other.add(
						MonophonyLockedGroupRow(
							{'title': _('All Videos'), 'contents': videos}, self.player
						)
					)
			for box in non_empty:
				self.pge_results.add(box)

		self.search_lock.unlock()
		return False
