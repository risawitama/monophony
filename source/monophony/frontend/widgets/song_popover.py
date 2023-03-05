import monophony.backend.cache
import monophony.backend.playlists

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Gio, GLib, Gtk, Pango


class MonophonySongPopover(Gtk.PopoverMenu):
	def __init__(self, btn: Gtk.MenuButton, player: object, song: dict = None, group: dict = None, editable: bool = False):
		super().__init__()

		song = song if song else player.get_current_song()
		self.player = player
		self.song = song
		self.group = group
		self.editable = editable

		window = btn.get_ancestor(Gtk.Window)
		menu = Gio.Menu()
		if editable:
			menu.append(_('Move Up'), 'move-song-up')
			menu.append(_('Move Down'), 'move-song-down')
			window.install_action(
				'move-song-up',
				None,
				lambda w, a, t: w._on_move_song(self.song, self.group, -1)
			)
			window.install_action(
				'move-song-down',
				None,
				lambda w, a, t: w._on_move_song(self.song, self.group, 1)
			)

			if monophony.backend.cache.is_song_being_cached(song['id']):
				pass
			elif monophony.backend.cache.is_song_cached(song['id']):
				menu.append(_('Remove From Downloads'), 'uncache-song')
				window.install_action(
					'uncache-song',
					None,
					lambda w, a, t: w._on_uncache_song(self.song)
				)
			else:
				menu.append(_('Download to Music Folder'), 'cache-song')
				window.install_action(
					'cache-song',
					None,
					lambda w, a, t: w._on_cache_song(self.song)
				)
		if player.get_current_song() != song:
			menu.append(_('Add to Queue'), 'queue-song')
			window.install_action(
				'queue-song',
				None,
				lambda w, a, t: w._on_queue_song(self.song)
			)
		menu.append(_('New Playlist...'), 'new-playlist')
		window.install_action(
			'new-playlist',
			None,
			lambda w, a, t: w._on_new_playlist(self.song)
		)
		itm_lists = Gio.MenuItem()
		itm_lists.set_attribute_value(
			'custom',  GLib.Variant.new_string('playlists')
		)
		sec_lists = Gio.Menu()
		sec_lists.append_item(itm_lists)
		self.set_menu_model(menu)

		playlists = monophony.backend.playlists.read_playlists()
		if playlists and song:
			menu.append_section(None, sec_lists)
			scr_playlists = Gtk.ScrolledWindow.new()
			scr_playlists.set_max_content_width(80)
			scr_playlists.set_max_content_height(80)
			scr_playlists.set_propagate_natural_height(True)
			scr_playlists.set_policy(
				Gtk.PolicyType.NEVER,
				Gtk.PolicyType.AUTOMATIC
			)
			box_playlists = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
			for name, songs in playlists.items():
				box_playlist = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
				box_playlist.set_spacing(5)
				chk_playlist = Gtk.CheckButton.new_with_label(name)
				chk_playlist.get_last_child().set_max_width_chars(20)
				chk_playlist.get_last_child().set_ellipsize(
					Pango.EllipsizeMode.END
				)
				chk_playlist.set_active(song['id'] in [s['id'] for s in songs])
				chk_playlist.connect('toggled', self._on_playlist_toggled, name)
				box_playlist.append(chk_playlist)
				box_playlists.append(box_playlist)

			scr_playlists.set_child(box_playlists)
			self.add_child(scr_playlists, 'playlists')
			btn.set_popover(self)
		else:
			btn.popdown()
			window._on_new_playlist()

	def _on_playlist_toggled(self, chk: Gtk.CheckButton, name: str):
		if chk.get_active():
			monophony.backend.playlists.add_song(self.song, name)
		else:
			monophony.backend.playlists.remove_song(self.song['id'], name)
			if self.editable and name == self.group['title']:
				self.popdown()
