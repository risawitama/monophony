import monophony.backend.cache
import monophony.backend.playlists

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gio, GLib, Gtk


class MonophonySongPopover(Gtk.PopoverMenu):
	def __init__(self, btn: Gtk.MenuButton, song: dict, parent):
		super().__init__()

		self.song = song
		self.window = btn.get_ancestor(Gtk.Window)
		self.parent_row = parent
		menu = Gio.Menu()

		if monophony.backend.cache.is_song_being_cached(song['id']):
			pass
		elif monophony.backend.cache.is_song_cached(song['id']):
			menu.append(_('Remove From Downloads'), 'uncache-song')
			self.window.install_action(
				'uncache-song', None, lambda *_: self._on_uncache(song)
			)
		else:
			menu.append(_('Download'), 'cache-song')
			self.window.install_action(
				'cache-song', None, lambda *_: self._on_cache(song)
			)

		menu.append(_('Add to...'), 'add-song-to')
		self.window.install_action(
			'add-song-to', None, lambda w, *_: w._on_add_clicked(song)
		)
		menu.append(_('View Artist'), 'show-artist')
		self.window.install_action(
			'show-artist', None, lambda w, *_: w._on_show_artist(song['author_id'])
		)
		self.set_menu_model(menu)
		btn.set_popover(self)

	def _on_cache(self, song):
		self.window._on_cache_song(song)
		self.parent_row.spinner.set_visible(True)
		GLib.timeout_add_seconds(1, self.parent_row.update_download_status)

	def _on_uncache(self, song):
		self.window._on_uncache_song(song)
		self.parent_row.spinner.set_visible(False)
		self.parent_row.checkmark.set_visible(False)
