import monophony.backend.yt
from monophony.frontend.widgets.group_row import MonophonyGroupRow
from monophony.frontend.widgets.song_row import MonophonySongRow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, GLib, Gtk


class MonophonySearchPage(Gtk.Box):
	def __init__(self):
		super().__init__(orientation = Gtk.Orientation.VERTICAL)

		ent_search = Gtk.SearchEntry()
		ent_search.set_margin_start(10)
		ent_search.set_margin_end(10)
		ent_search.set_margin_bottom(10)
		ent_search.connect(
			'activate',
			lambda e: GLib.Thread.new(None, self._on_search, e)
		)

		clm_search = Adw.Clamp()
		clm_search.set_child(ent_search)

		self.box_results = Adw.PreferencesPage()

		clm_results = Adw.Clamp()
		clm_results.set_vexpand(True)
		clm_results.set_valign(Gtk.Align.FILL)
		clm_results.set_child(self.box_results)

		scr_results = Gtk.ScrolledWindow()
		scr_results.set_vexpand(True)
		scr_results.set_valign(Gtk.Align.FILL)
		scr_results.set_child(clm_results)

		self.set_vexpand(True)
		self.set_valign(Gtk.Align.FILL)
		self.set_margin_top(10)
		self.append(clm_search)
		self.append(scr_results)

		self.search_results = []
		self.results_changed = False
		self.search_lock = GLib.Mutex()

		GLib.timeout_add(100, self.update_results)

	def _on_search(self, ent: Gtk.SearchEntry):
		self.search_lock.lock()
		self.search_results = monophony.backend.yt.search(ent.get_text())
		self.results_changed = True
		self.search_lock.unlock()

	def update_results(self) -> True:
		if not self.search_lock.trylock():
			return True

		if self.results_changed:
			self.results_changed = False
			top = self.box_results.get_first_child().get_first_child().get_first_child().get_first_child()
			while child := top.get_first_child():
				self.box_results.remove(child)

			if not self.search_results:
				pge_empty = Adw.StatusPage()
				pge_empty.set_vexpand(True)
				pge_empty.set_valign(Gtk.Align.FILL)
				pge_empty.set_title(_('No results'))
				pge_empty.set_icon_name('system-search-symbolic')
				self.box_results.add(pge_empty)
			else:
				box_songs = Adw.PreferencesGroup.new()
				box_songs.set_title(_('Songs'))
				box_albums = Adw.PreferencesGroup.new()
				box_albums.set_title(_('Albums'))
				box_videos = Adw.PreferencesGroup.new()
				box_videos.set_title(_('Videos'))
				for item in self.search_results:
					if item['type'] == 'song':
						box_songs.add(MonophonySongRow(item))
					elif item['type'] == 'video':
						box_videos.add(MonophonySongRow(item))
					elif item['type'] == 'album':
						pass
				for box in {box_songs, box_videos, box_albums}:
					self.box_results.add(box)

		self.search_lock.unlock()
		return True
