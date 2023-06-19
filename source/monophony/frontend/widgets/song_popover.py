import monophony.backend.cache
import monophony.backend.playlists

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gio, Gtk


class MonophonySongPopover(Gtk.PopoverMenu):
	def __init__(self, btn: Gtk.MenuButton, song: dict, group: dict = None):
		super().__init__()

		window = btn.get_ancestor(Gtk.Window)
		menu = Gio.Menu()
		window.install_action(
			'move-song-up',
			None,
			lambda w, a, t: w._on_move_song(song, group, -1)
		)
		window.install_action(
			'move-song-down',
			None,
			lambda w, a, t: w._on_move_song(song, group, 1)
		)

		if monophony.backend.cache.is_song_being_cached(song['id']):
			pass
		elif monophony.backend.cache.is_song_cached(song['id']):
			menu.append(_('Remove From Downloads'), 'uncache-song')
			window.install_action(
				'uncache-song',
				None,
				lambda w, a, t: w._on_uncache_song(song)
			)
		else:
			menu.append(_('Download to Music Folder'), 'cache-song')
			window.install_action(
				'cache-song',
				None,
				lambda w, a, t: w._on_cache_song(song)
			)

		if group:
			menu.append(_('Remove From Playlist'), 'remove-song')
			window.install_action(
				'remove-song',
				None,
				lambda w, a, t: w._on_remove_song(song['id'], group['title'])
			)

		menu.append(_('Add to...'), 'add-song-to')
		window.install_action(
			'add-song-to',
			None,
			lambda w, a, t: w._on_add_clicked(song)
		)
		menu.append(_('Show Artist'), 'show-artist')
		window.install_action(
			'show-artist',
			None,
			lambda w, a, t: w._on_show_artist(song['author_id'])
		)
		self.set_menu_model(menu)
		btn.set_popover(self)
