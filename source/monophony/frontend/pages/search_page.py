import monophony.backend.yt
from monophony.frontend.widgets.group_row import MonophonyGroupRow
from monophony.frontend.widgets.song_row import MonophonySongRow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, GLib, Gtk


class MonophonySearchPage(Gtk.Box):
	def __init__(self, player: object):
		super().__init__(orientation = Gtk.Orientation.VERTICAL)

		ent_search = Gtk.SearchEntry()
		ent_search.set_margin_start(10)
		ent_search.set_margin_end(10)
		ent_search.set_margin_bottom(10)
		ent_search.connect('activate', self._on_search)

		clm_search = Adw.Clamp()
		clm_search.set_child(ent_search)
		self.append(clm_search)

		self.box_results = Adw.PreferencesPage()
		self.append(self.box_results)
		self.box_results.hide()

		self.pge_status = Adw.StatusPage()
		self.pge_status.set_vexpand(True)
		self.pge_status.set_valign(Gtk.Align.FILL)
		self.pge_status.set_icon_name('system-search-symbolic')
		self.append(self.pge_status)

		spn_loading = Gtk.Spinner.new()
		spn_loading.set_halign(Gtk.Align.CENTER)
		spn_loading.set_valign(Gtk.Align.CENTER)
		spn_loading.set_vexpand(True)
		spn_loading.set_spinning(True)
		self.box_loading = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		self.box_loading.set_margin_bottom(10)
		self.box_loading.append(spn_loading)
		self.append(self.box_loading)
		self.box_loading.hide()

		self.set_margin_top(10)
		self.set_vexpand(True)
		self.search_results = []
		self.results_changed = False
		self.search_lock = GLib.Mutex()
		self.player = player

		GLib.timeout_add(100, self.update_results)

	def _on_search(self, ent: Gtk.SearchEntry):
		if not self.search_lock.trylock():
			return

		top = self.box_results.get_first_child().get_first_child().get_first_child().get_first_child()
		while child := top.get_first_child():
			self.box_results.remove(child)
		self.pge_status.hide()
		self.box_loading.show()

		self.search_lock.unlock()
		GLib.Thread.new(None, self.do_search, ent.get_text())

	def do_search(self, query: str):
		self.search_lock.lock()
		self.search_results = monophony.backend.yt.search(query)
		self.results_changed = True
		self.search_lock.unlock()

	def update_results(self) -> True:
		if not self.search_lock.trylock():
			return True

		if self.results_changed:
			self.results_changed = False

			self.box_loading.hide()
			if not self.search_results:
				self.pge_status.set_title(_('No results'))
				self.pge_status.show()
				self.box_results.hide()
			else:
				self.pge_status.hide()
				self.box_results.show()
				box_songs = Adw.PreferencesGroup.new()
				box_songs.set_title(_('Songs'))
				box_albums = Adw.PreferencesGroup.new()
				box_albums.set_title(_('Albums'))
				box_videos = Adw.PreferencesGroup.new()
				box_videos.set_title(_('Videos'))
				for item in self.search_results:
					if item['type'] == 'song':
						box_songs.add(MonophonySongRow(item, self.player))
					elif item['type'] == 'video':
						box_videos.add(MonophonySongRow(item, self.player))
					elif item['type'] == 'album':
						box_albums.add(MonophonyGroupRow(item, self.player))
				for box in {box_songs, box_videos, box_albums}:
					self.box_results.add(box)

		self.search_lock.unlock()
		return True
