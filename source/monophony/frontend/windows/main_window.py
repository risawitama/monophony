import monophony.backend.cache
import monophony.backend.mpris
import monophony.backend.player
import monophony.backend.playlists
import monophony.backend.settings
from monophony import __version__, APP_ID
from monophony.frontend.pages.library_page import MonophonyLibraryPage
from monophony.frontend.pages.search_page import MonophonySearchPage
from monophony.frontend.widgets.player import MonophonyPlayer
from monophony.frontend.windows.rename_window import MonophonyRenameWindow
from monophony.frontend.windows.message_window import MonophonyMessageWindow
from monophony.frontend.windows.add_window import MonophonyAddWindow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, GLib, Gtk


class MonophonyMainWindow(Adw.ApplicationWindow):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.set_default_size(
			int(monophony.backend.settings.get_value('window-width', 600)),
			int(monophony.backend.settings.get_value('window-height', 500))
		)
		self.set_title('Monophony')
		self.set_icon_name(APP_ID)
		self.player = monophony.backend.player.Player()
		self.removed_playlists = []
		GLib.Thread.new(None, monophony.backend.mpris.init, self.player)

		self.stack = Adw.Leaflet()
		self.stack.set_can_navigate_forward(False)
		self.stack.set_can_navigate_back(False)
		self.stack.set_can_unfold(False)
		pge_library = MonophonyLibraryPage(self.player)
		lfp_library = self.stack.append(pge_library)
		lfp_library.set_navigatable(True)
		lfp_library.set_name('library')
		self.pge_search = MonophonySearchPage(self.player)
		lfp_search = self.stack.append(self.pge_search)
		lfp_search.set_navigatable(True)
		lfp_search.set_name('search')
		self.stack.set_visible_child(pge_library)

		self.toaster = Adw.ToastOverlay.new()
		self.toaster.set_child(self.stack)

		self.btn_back = Gtk.Button.new_from_icon_name('go-previous-symbolic')
		self.btn_back.set_tooltip_text(_('Go back'))
		self.btn_back.set_visible(False)
		self.btn_back.connect('clicked', self._on_back_clicked)

		btn_about = Gtk.Button.new_from_icon_name('help-about-symbolic')
		btn_about.set_tooltip_text(_('About'))
		btn_about.set_has_frame(False)
		btn_about.connect('clicked', self._on_about_clicked)

		self.ent_search = Gtk.SearchEntry()
		self.ent_search.set_property('placeholder-text', _('Search for Content...'))
		self.ent_search.set_hexpand(True)
		self.ent_search.set_halign(Gtk.Align.FILL)
		self.ent_search.connect('activate', self._on_search)
		clm_search = Adw.Clamp.new()
		clm_search.set_child(self.ent_search)

		header_bar = Adw.HeaderBar()
		header_bar.pack_start(self.btn_back)
		header_bar.set_title_widget(clm_search)
		header_bar.pack_end(btn_about)

		self.player_revealer = Gtk.Revealer()
		self.player_revealer.set_property('overflow', Gtk.Overflow.VISIBLE)
		self.player_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
		self.player_revealer.set_child(MonophonyPlayer(self, self.player))

		box_content = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		box_content.append(header_bar)
		box_content.append(self.toaster)
		box_content.append(self.player_revealer)
		self.set_content(box_content)

		self.install_action(
			'quit-app', None, (lambda w, *_: w.close())
		)
		self.install_action(
			'focus-search', None, (lambda w, *_: w.ent_search.grab_focus())
		)
		self.install_action(
			'playlist-delete-undo', None, (lambda w, *_: w._on_undo_deletion())
		)
		self.get_application().set_accels_for_action('quit-app', ['<Control>w', '<Control>q'])
		self.get_application().set_accels_for_action('focus-search', ['<Control>f'])
		self.connect('close-request', MonophonyMainWindow._on_quit)

	def _on_quit(self):
		size = self.get_default_size()
		monophony.backend.settings.set_value('window-width', size.width)
		monophony.backend.settings.set_value('window-height', size.height)

	def _on_search(self, ent: Gtk.Entry):
		self.stack.set_visible_child_name('search')
		self.btn_back.set_visible(True)
		self.pge_search._on_search(ent)

	def _on_show_artist(self, artist_id: str):
		self.stack.set_visible_child_name('search')
		self.btn_back.set_visible(True)
		self.pge_search.show_artist(artist_id)

	def _on_back_clicked(self, _b):
		self.pge_search.go_back()
		if not self.pge_search.results_pages:
			self.stack.set_visible_child_name('library')
			self.btn_back.set_visible(False)
			self.ent_search.set_text('')

	def _on_about_clicked(self, _b):
		win_about = Adw.AboutWindow.new()
		win_about.set_application_icon(APP_ID)
		win_about.set_application_name('Monophony')
		win_about.set_version(__version__)
		win_about.set_copyright('Copyright © 2022-2023 zehkira')
		win_about.set_license_type(Gtk.License.AGPL_3_0)
		win_about.add_legal_section(
			'ytmusicapi', 'Copyright © 2020 sigma67', Gtk.License.MIT_X11
		)
		win_about.add_legal_section(
			'mpris_server','Copyright © Alex DeLorenzo', Gtk.License.AGPL_3_0
		)
		win_about.add_legal_section(
			'Requests', 'Copyright © 2019 Kenneth Reitz', Gtk.License.APACHE_2_0
		)
		win_about.set_translator_credits(_('translator-credits'))
		win_about.set_issue_url('https://gitlab.com/zehkira/monophony/-/issues')
		win_about.set_website('https://gitlab.com/zehkira/monophony')
		win_about.set_transient_for(self)
		win_about.present()

	def _on_add_clicked(self, song: dict):
		popup = MonophonyAddWindow(song, self.player)
		popup.set_transient_for(self)
		popup.present()

	def _on_remove_song(self, song: str, playlist: str):
		monophony.backend.playlists.remove_song(song, playlist)

	def _on_move_song(self, song: dict, group: dict, direction: int):
		index = group['contents'].index(song)
		monophony.backend.playlists.swap_songs(
			group['title'], index, index + direction
		)

	def _on_uncache_song(self, song: dict):
		monophony.backend.cache.uncache_song(song['id'])

	def _on_cache_song(self, song: dict):
		GLib.Thread.new(
			None, monophony.backend.cache.cache_songs, [song['id']]
		)

	def _on_cache_playlist(self, songs: list):
		GLib.Thread.new(
			None, monophony.backend.cache.cache_songs, [s['id'] for s in songs]
		)

	def _on_delete_playlist(self, widget: object):
		self.removed_playlists.insert(0, widget.group)
		toast_undo = Adw.Toast.new(
			_('Deleted "{playlist_name}"').format(playlist_name=widget.group['title'])
		)
		toast_undo.set_button_label(_('Undo'))
		toast_undo.set_action_name('playlist-delete-undo')
		toast_undo.connect('dismissed', self._on_toast_dismissed)
		self.toaster.add_toast(toast_undo)
		monophony.backend.playlists.remove_playlist(widget.group['title'])

	def _on_toast_dismissed(self, _toast: object):
		self.removed_playlists.pop()

	def _on_undo_deletion(self):
		playlist = self.removed_playlists[len(self.removed_playlists) - 1]
		monophony.backend.playlists.add_playlist(playlist['title'], playlist['contents'])

	def _on_duplicate_playlist(self, widget: object):
		monophony.backend.playlists.add_playlist(
			widget.group['title'], widget.group['contents']
		)

	def _on_rename_playlist(self, widget: object):
		def _rename(new_name: str):
			success = monophony.backend.playlists.rename_playlist(
				widget.group['title'], new_name
			)
			if success:
				widget.group['title'] = new_name
				widget.set_title(new_name)
			else:
				MonophonyMessageWindow(
					self,
					_('Could not Rename'),
					_('Playlist already exists')
				).present()

		popup = MonophonyRenameWindow(self, _rename, widget.group['title'])
		popup.present()

	def _on_save_playlist(self, name: str, contents: list):
		monophony.backend.playlists.add_playlist(name, contents)
		self.toaster.add_toast(Adw.Toast.new(_('Added')))
