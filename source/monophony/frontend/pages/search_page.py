import monophony.backend.yt
from monophony.frontend.widgets.group_row import MonophonyGroupRow
from monophony.frontend.widgets.song_row import MonophonySongRow
from monophony.frontend.widgets.artist_row import MonophonyArtistRow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, GLib, GObject, Gtk


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
		self.box_loading = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		self.box_loading.set_margin_bottom(10)
		self.box_loading.append(spn_loading)
		self.box_loading.bind_property(
			'visible',
			spn_loading,
			'spinning',
			GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL
		)
		self.append(self.box_loading)
		self.box_loading.set_visible(False)

		self.set_vexpand(True)
		self.query = ''
		self.results_pages = []
		self.results = []
		self.results_filterable = False
		self.results_changed = False
		self.search_lock = GLib.Mutex()
		self.player = player

		GLib.timeout_add(1000, self.update_results)

	def _on_search(self, ent: Gtk.SearchEntry):
		if not self.search_lock.trylock():
			return

		self.pge_status.set_visible(False)
		if self.results_pages:
			self.results_pages[-1].set_visible(False)
		self.box_loading.set_visible(True)

		self.search_lock.unlock()
		GLib.Thread.new(None, self.do_search, ent.get_text())

	def do_search(self, query: str, filter_: str = ''):
		self.search_lock.lock()
		self.query = query
		self.results = monophony.backend.yt.search(query, filter_)

		box_results = Adw.PreferencesPage()
		box_results.set_vexpand(True)
		self.append(box_results)
		box_results.set_visible(False)
		if not filter_:
			self.results_filterable = True
			for page in self.results_pages:
				self.remove(page)
			self.results_pages = [box_results]
		else:
			self.results_filterable = False
			self.results_pages.append(box_results)

		self.results_changed = True
		self.search_lock.unlock()

	def show_more(self, category: str):
		self.results_pages[-1].set_visible(False)
		self.pge_status.set_visible(False)
		self.box_loading.set_visible(True)
		GLib.Thread.new(None, self.do_search, self.query, category)

	def do_get_artist(self, artist_id: str):
		self.search_lock.lock()
		results = monophony.backend.yt.get_artist(artist_id)
		if not results:
			self.pge_status.set_visible(True)
			self.box_loading.set_visible(False)
			self.search_lock.unlock()
			return

		self.results = results
		self.results_filterable = False

		box_results = Adw.PreferencesPage()
		box_results.set_vexpand(True)
		self.append(box_results)
		box_results.set_visible(False)
		self.results_pages.append(box_results)
		self.results_changed = True
		self.search_lock.unlock()

	def show_artist(self, artist_id: str):
		if self.results_pages:
			self.results_pages[-1].set_visible(False)
		self.pge_status.set_visible(False)
		self.box_loading.set_visible(True)
		GLib.Thread.new(None, self.do_get_artist, artist_id)

	def go_back(self):
		self.search_lock.lock()
		if self.results_pages:
			self.remove(self.results_pages[-1])
			self.results_pages = self.results_pages[:-1]
		self.box_loading.set_visible(False)
		self.pge_status.set_visible(False)
		if self.results_pages:
			self.results_pages[-1].set_visible(True)
		self.results = []
		self.results_changed = False
		self.search_lock.unlock()

	def update_results(self) -> True:
		if not self.search_lock.trylock():
			return True

		if self.results_changed:
			self.results_changed = False
			self.box_loading.set_visible(False)
			self.pge_status.set_visible(len(self.results) == 0)
			if not self.results:
				self.pge_status.set_title(_('No Results'))
			else:
				self.results_pages[-1].set_visible(True)
				box_top = Adw.PreferencesGroup.new()
				box_songs = Adw.PreferencesGroup.new()
				box_videos = Adw.PreferencesGroup.new()
				box_albums = Adw.PreferencesGroup.new()
				box_playlists = Adw.PreferencesGroup.new()
				box_artists = Adw.PreferencesGroup.new()
				box_top.set_title(_('Top Result'))
				box_songs.set_title(_('Songs'))
				box_albums.set_title(_('Albums'))
				box_videos.set_title(_('Videos'))
				box_artists.set_title(_('Artists'))

				if self.results_filterable:
					btn_more = Gtk.Button.new_with_label(_('More'))
					btn_more.connect(
						'clicked',
						lambda _b, f: self.show_more(f),
						'songs'
					)
					box_songs.set_header_suffix(btn_more)

					btn_more = Gtk.Button.new_with_label(_('More'))
					btn_more.connect(
						'clicked',
						lambda _b, f: self.show_more(f),
						'albums'
					)
					box_albums.set_header_suffix(btn_more)

					box_playlists.set_title(_('Community Playlists'))
					btn_more = Gtk.Button.new_with_label(_('More'))
					btn_more.connect(
						'clicked',
						lambda _b, f: self.show_more(f),
						'playlists'
					)
					box_playlists.set_header_suffix(btn_more)

					btn_more = Gtk.Button.new_with_label(_('More'))
					btn_more.connect(
						'clicked',
						lambda _b, f: self.show_more(f),
						'videos'
					)
					box_videos.set_header_suffix(btn_more)

					btn_more = Gtk.Button.new_with_label(_('More'))
					btn_more.connect(
						'clicked',
						lambda _b, f: self.show_more(f),
						'artists'
					)
					box_artists.set_header_suffix(btn_more)

				non_empty = []
				for item in self.results:
					if item['type'] == 'song':
						if item['top']:
							box_top.add(MonophonySongRow(item, self.player))
							non_empty.append(box_top)
							continue
						box_songs.add(MonophonySongRow(item, self.player))
						if box_songs not in non_empty:
							non_empty.append(box_songs)
					elif item['type'] == 'video':
						if item['top']:
							box_top.add(MonophonySongRow(item, self.player))
							non_empty.append(box_top)
							continue
						box_videos.add(MonophonySongRow(item, self.player))
						if box_videos not in non_empty:
							non_empty.append(box_videos)
					elif item['type'] == 'album':
						if item['top']:
							box_top.add(MonophonyGroupRow(item, self.player))
							non_empty.append(box_top)
							continue
						box_albums.add(MonophonyGroupRow(item, self.player))
						if box_albums not in non_empty:
							non_empty.append(box_albums)
					elif item['type'] == 'playlist':
						if item['top']:
							box_top.add(MonophonyGroupRow(item, self.player))
							non_empty.append(box_top)
							continue
						box_playlists.add(MonophonyGroupRow(item, self.player))
						if box_playlists not in non_empty:
							non_empty.append(box_playlists)
					elif item['type'] == 'artist':
						if item['top']:
							box_top.add(MonophonyArtistRow(item, self))
							non_empty.append(box_top)
							continue
						box_artists.add(MonophonyArtistRow(item, self))
						if box_artists not in non_empty:
							non_empty.append(box_artists)
				for box in non_empty:
					self.results_pages[-1].add(box)
				self.results_pages[-1].get_first_child().get_vadjustment().set_value(0)

		self.search_lock.unlock()
		return True
