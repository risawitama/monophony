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

		self.pge_status = Adw.StatusPage()
		self.pge_status.set_vexpand(True)
		self.pge_status.set_valign(Gtk.Align.FILL)
		self.pge_status.set_icon_name('system-search-symbolic')
		self.pge_status.set_title(_('No Results'))
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

		self.set_vexpand(True)
		self.query = ''
		self.results_pages = []
		self.results = []
		self.results_changed = False
		self.search_lock = GLib.Mutex()
		self.player = player

		GLib.timeout_add(1000, self.update_results)

	def _on_search(self, ent: Gtk.SearchEntry):
		if not self.search_lock.trylock():
			return

		self.pge_status.hide()
		if self.results_pages:
			self.results_pages[-1].hide()
		self.box_loading.show()

		self.search_lock.unlock()
		GLib.Thread.new(None, self.do_search, ent.get_text())

	def do_search(self, query: str, filter_: str = ''):
		self.search_lock.lock()
		self.query = query
		self.results = monophony.backend.yt.search(query, filter_)

		box_results = Adw.PreferencesPage()
		box_results.set_vexpand(True)
		self.append(box_results)
		box_results.hide()
		if not filter_:
			for page in self.results_pages:
				self.remove(page)
			self.results_pages = [box_results]
		else:
			self.results_pages.append(box_results)

		self.results_changed = True
		self.search_lock.unlock()

	def show_more(self, category: str):
		self.results_pages[-1].hide()
		self.pge_status.hide()
		self.box_loading.show()
		GLib.Thread.new(None, self.do_search, self.query, category)

	def go_back(self):
		self.search_lock.lock()
		self.remove(self.results_pages[-1])
		self.results_pages = self.results_pages[:-1]
		self.box_loading.hide()
		if self.results_pages:
			self.results_pages[-1].show()
		self.results = []
		self.results_changed = False
		self.search_lock.unlock()

	def update_results(self) -> True:
		if not self.search_lock.trylock():
			return True

		if self.results_changed:
			self.results_changed = False
			self.box_loading.hide()
			if not self.results:
				self.pge_status.set_title(_('No Results'))
				self.pge_status.show()
			else:
				self.pge_status.hide()
				self.results_pages[-1].show()
				box_songs = Adw.PreferencesGroup.new()
				box_videos = Adw.PreferencesGroup.new()
				box_albums = Adw.PreferencesGroup.new()
				box_playlists = Adw.PreferencesGroup.new()

				if len(self.results_pages) == 1:
					box_songs.set_title(_('Songs'))
					btn_more = Gtk.Button.new_with_label(_('More'))
					btn_more.connect(
						'clicked',
						lambda b, f: self.show_more(f),
						'songs'
					)
					box_songs.set_header_suffix(btn_more)

					box_albums.set_title(_('Albums'))
					btn_more = Gtk.Button.new_with_label(_('More'))
					btn_more.connect(
						'clicked',
						lambda b, f: self.show_more(f),
						'albums'
					)
					box_albums.set_header_suffix(btn_more)

					box_playlists.set_title(_('Community Playlists'))
					btn_more = Gtk.Button.new_with_label(_('More'))
					btn_more.connect(
						'clicked',
						lambda b, f: self.show_more(f),
						'playlists'
					)
					box_playlists.set_header_suffix(btn_more)

					box_videos.set_title(_('Videos'))
					btn_more = Gtk.Button.new_with_label(_('More'))
					btn_more.connect(
						'clicked',
						lambda b, f: self.show_more(f),
						'videos'
					)
					box_videos.set_header_suffix(btn_more)

				non_empty = []
				for item in self.results:
					if item['type'] == 'song':
						box_songs.add(MonophonySongRow(item, self.player))
						if box_songs not in non_empty:
							non_empty.append(box_songs)
					elif item['type'] == 'video':
						box_videos.add(MonophonySongRow(item, self.player))
						if box_videos not in non_empty:
							non_empty.append(box_videos)
					elif item['type'] == 'album':
						box_albums.add(MonophonyGroupRow(item, self.player))
						if box_albums not in non_empty:
							non_empty.append(box_albums)
					elif item['type'] == 'playlist':
						box_playlists.add(MonophonyGroupRow(item, self.player))
						if box_playlists not in non_empty:
							non_empty.append(box_playlists)
				for box in non_empty:
					self.results_pages[-1].add(box)
				self.results_pages[-1].get_first_child().get_vadjustment().set_value(0)

		self.search_lock.unlock()
		return True
