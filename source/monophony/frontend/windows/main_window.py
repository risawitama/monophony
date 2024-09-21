import monophony.backend.cache
import monophony.backend.mpris
import monophony.backend.player
import monophony.backend.playlists
import monophony.backend.settings
from monophony import __version__, APP_ID
from monophony.frontend.tabs.library_tab import MonophonyLibraryTab
from monophony.frontend.tabs.queue_tab import MonophonyQueueTab
from monophony.frontend.tabs.search_tab import MonophonySearchTab
from monophony.frontend.widgets.player import MonophonyPlayer
from monophony.frontend.windows.add_window import MonophonyAddWindow
from monophony.frontend.windows.import_window import MonophonyImportWindow

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
		self.player.queue_end_callback = self._on_queue_end
		self.removed_playlists = []
		GLib.Thread.new(None, monophony.backend.mpris.init, self.player)

		self.stack = Adw.ViewStack()
		self.library_tab = MonophonyLibraryTab(self.player)
		self.stack.add_titled_with_icon(
			self.library_tab, 'library', _('Library'), 'emblem-music-symbolic'
		)
		self.stack.add_titled_with_icon(
			MonophonySearchTab(self.player),
			'search',
			_('Search'),
			'system-search-symbolic'
		)
		self.stack.add_titled_with_icon(
			MonophonyQueueTab(self.player),
			'queue',
			_('Queue'),
			'view-list-symbolic'
		)
		self.stack.set_visible_child_name('library')

		self.toaster = Adw.ToastOverlay.new()
		self.toaster.set_child(self.stack)

		btn_about = Gtk.Button.new_from_icon_name('help-about-symbolic')
		btn_about.set_tooltip_text(_('About'))
		btn_about.connect('clicked', lambda _b: self._on_about_clicked())

		switcher = Adw.ViewSwitcher()
		switcher.set_stack(self.stack)

		header_bar = Adw.HeaderBar()
		header_bar.set_title_widget(switcher)
		header_bar.pack_start(btn_about)

		self.toolbar_view = Adw.ToolbarView()
		self.toolbar_view.add_top_bar(header_bar)
		self.toolbar_view.add_bottom_bar(MonophonyPlayer(self, self.player))
		self.toolbar_view.set_content(self.toaster)
		self.toolbar_view.set_reveal_bottom_bars(False)
		self.set_content(self.toolbar_view)

		self.install_action(
			'quit-app', None, (lambda w, *_: w._on_quit())
		)
		self.install_action(
			'focus-library',
			None,
			(lambda w, *_: w.stack.set_visible_child_name('library'))
		)
		self.install_action(
			'focus-search',
			None,
			(lambda w, *_: w._on_search())
		)
		self.install_action(
			'focus-queue',
			None,
			(lambda w, *_: w.stack.set_visible_child_name('queue'))
		)
		self.install_action(
			'playlist-delete-undo', None, (lambda w, *_: w._on_undo_deletion())
		)
		self.get_application().set_accels_for_action(
			'quit-app', ['<Control>w', '<Control>q']
		)
		self.get_application().set_accels_for_action('focus-library', ['<Alt>1'])
		self.get_application().set_accels_for_action(
			'focus-search', ['<Control>f', '<Alt>2']
		)
		self.get_application().set_accels_for_action('focus-queue', ['<Alt>3'])
		self.connect('close-request', MonophonyMainWindow.run_background)

	def append_page(self, widget: Gtk.Widget):
		while child := self.stack.get_adjacent_child(Adw.NavigationDirection.FORWARD):
			self.stack.remove(child)

		self.stack.append(widget)
		self.stack.navigate(Adw.NavigationDirection.FORWARD)

	def run_background(self) -> bool:
		if self.player.get_current_song():
			self.set_visible(False)
			return True

		self._on_quit()
		return False

	def _on_quit(self):
		self.player.terminate()
		size = self.get_default_size()
		monophony.backend.settings.set_value('window-width', size.width)
		monophony.backend.settings.set_value('window-height', size.height)
		self.get_application().quit()

	def _on_search(self):
		self.stack.set_visible_child_name('search')
		self.stack.get_visible_child().ent_search.grab_focus()

	def _on_show_more(self, query: str, filter_: str):
		self.stack.set_visible_child_name('search')
		self.stack.get_visible_child().show_more(query, filter_)

	def _on_show_artist(self, artist: str):
		self.stack.set_visible_child_name('search')
		self.stack.get_visible_child().show_artist(artist)

	def _on_about_clicked(self):
		win_about = Adw.AboutWindow.new()
		win_about.set_application_icon(APP_ID)
		win_about.set_application_name('Monophony')
		win_about.set_version(__version__)
		win_about.set_copyright('Copyright © 2022-present Zehkira')
		win_about.set_license_type(Gtk.License.AGPL_3_0)
		win_about.add_legal_section(
			'ytmusicapi', 'Copyright © 2024 sigma67', Gtk.License.MIT_X11
		)
		win_about.add_legal_section(
			'mpris_server', 'Copyright © Alex DeLorenzo', Gtk.License.LGPL_3_0
		)
		win_about.set_translator_credits(_('translator-credits'))
		win_about.set_issue_url('https://gitlab.com/zehkira/monophony/-/issues')
		win_about.set_website('https://gitlab.com/zehkira/monophony')
		win_about.set_transient_for(self)
		win_about.present()

	def _on_import_clicked(self, url: str='', group: list | None = None):
		popup = MonophonyImportWindow(url=url, group=group)
		popup.set_transient_for(self)
		popup.present()

	def _on_add_clicked(self, song: dict):
		popup = MonophonyAddWindow(
			song, self.player, self.library_tab.update_playlists
		)
		popup.set_transient_for(self)
		popup.present()

	def _on_remove_song(self, song: str, playlist: str):
		monophony.backend.playlists.remove_song(song, playlist)
		self.library_tab.update_playlists()

	def _on_move_song(self, song: dict, group: dict, direction: int):
		index = group['contents'].index(song)
		monophony.backend.playlists.swap_songs(
			group['title'], index, index + direction
		)
		self.library_tab.update_playlists()

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

	def _on_delete_playlist(self, widget: object, local: bool=True):
		group = widget.group.copy()
		group['local'] = local
		self.removed_playlists.append(group)
		toast_undo = Adw.Toast.new(
			_('Deleted "{playlist_name}"').format(playlist_name=group['title'])
		)
		toast_undo.set_priority(Adw.ToastPriority.HIGH)
		toast_undo.set_button_label(_('Undo'))
		toast_undo.set_action_name('playlist-delete-undo')
		toast_undo.connect('dismissed', self._on_toast_dismissed)
		self.toaster.add_toast(toast_undo)
		if local:
			monophony.backend.playlists.remove_playlist(group['title'])
		else:
			monophony.backend.playlists.remove_external_playlist(group['title'])

	def _on_toast_dismissed(self, _toast: object):
		self.removed_playlists.pop()

	def _on_undo_deletion(self):
		playlist = self.removed_playlists[len(self.removed_playlists) - 1]
		if playlist['local']:
			monophony.backend.playlists.add_playlist(
				playlist['title'], playlist['contents']
			)
		else:
			monophony.backend.playlists.add_external_playlist(playlist)

	def _on_duplicate_playlist(self, widget: object):
		monophony.backend.playlists.add_playlist(
			widget.group['title'], widget.group['contents']
		)

	def _on_save_playlist(self, name: str, contents: list):
		monophony.backend.playlists.add_playlist(name, contents)
		self.toaster.add_toast(Adw.Toast.new(_('Added')))

	def _on_queue_end(self):
		if not self.is_visible():
			self._on_quit()
