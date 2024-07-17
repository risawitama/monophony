import monophony.backend.yt
from monophony.frontend.rows.importable_group_row import MonophonyImportableGroupRow
from monophony.frontend.rows.song_row import MonophonySongRow
from monophony.frontend.rows.artist_row import MonophonyArtistRow
from monophony.frontend.widgets.big_spinner import MonophonyBigSpinner

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, GLib, Gtk


class MonophonyResultsPage(Gtk.Box):
	def __init__(self, player: object, query: str='', filter_: str=''):
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
		self.box_loading.set_visible(bool(query))
		self.append(self.box_loading)

		self.set_vexpand(True)
		self.query = query
		self.filter = filter_
		self.results = []
		self.player = player

		if query:
			GLib.Thread.new('search', self.do_search)
		else:
			self.pge_status.set_visible(True)
			self.pge_status.set_title('')

	def do_search(self):
		self.results = monophony.backend.yt.search(self.query, self.filter)
		GLib.idle_add(self.await_results)

	def await_results(self) -> bool:
		def create_result_box(result_type: str, filtered: bool):
			box = Adw.PreferencesGroup.new()
			if not filtered:
				img_icon = Gtk.Image.new_from_icon_name('go-next-symbolic')
				lbl_text = Gtk.Label.new(_('Show All'))
				box_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
				box_btn.set_spacing(8)
				box_btn.append(lbl_text)
				box_btn.append(img_icon)
				btn_more = Gtk.Button()
				btn_more.add_css_class('suggested-action')
				btn_more.set_child(box_btn)
				btn_more.connect(
					'clicked',
					lambda _b, f: window._on_show_more(self.query, f),
					result_type
				)
				box.set_header_suffix(btn_more)
			return box

		self.box_loading.set_visible(False)
		self.pge_status.set_visible(len(self.results) == 0)
		if self.results:
			self.pge_results.set_visible(True)
			box_top = Adw.PreferencesGroup.new()
			box_songs = create_result_box('songs', self.filter != '')
			box_videos = create_result_box('videos', self.filter != '')
			box_albums = create_result_box('albums', self.filter != '')
			box_playlists = create_result_box('playlists', self.filter != '')
			box_artists = create_result_box('artists', self.filter != '')
			box_top.set_title(_('Top Result'))
			box_songs.set_title(_('Songs'))
			box_albums.set_title(_('Albums'))
			box_videos.set_title(_('Videos'))
			box_playlists.set_title(_('Community Playlists'))
			box_artists.set_title(_('Artists'))
			window = self.get_ancestor(Gtk.Window)

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
						box_top.add(MonophonyImportableGroupRow(item, self.player))
						non_empty.append(box_top)
						continue
					box_albums.add(MonophonyImportableGroupRow(item, self.player))
					if box_albums not in non_empty:
						non_empty.append(box_albums)
				elif item['type'] == 'playlist':
					if item['top']:
						box_top.add(MonophonyImportableGroupRow(item, self.player))
						non_empty.append(box_top)
						continue
					box_playlists.add(MonophonyImportableGroupRow(item, self.player))
					if box_playlists not in non_empty:
						non_empty.append(box_playlists)
				elif item['type'] == 'artist':
					if item['top']:
						box_top.add(MonophonyArtistRow(item))
						non_empty.append(box_top)
						continue
					box_artists.add(MonophonyArtistRow(item))
					if box_artists not in non_empty:
						non_empty.append(box_artists)
			for box in non_empty:
				self.pge_results.add(box)

		return False
