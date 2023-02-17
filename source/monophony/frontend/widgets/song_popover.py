import monophony.backend.cache
import monophony.backend.playlists
from monophony.frontend.windows.rename_window import MonophonyRenameWindow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gio, GLib, Gtk, Pango


class MonophonySongPopover(Gio.Menu):
	def __init__(self, btn: Gtk.MenuButton, player: object, song: dict = None, group: dict = None, editable: bool = False):
		super().__init__()

		song = song if song else player.get_current_song()
		self.player = player
		self.song = song
		self.group = group
		self.editable = editable
		self.ancestor = btn.get_ancestor(Adw.ActionRow)

		actions = Gio.Menu()
		self.append_section(None, actions)
		if editable:
			act = Gio.SimpleAction.new('app.moveup', None)
			act.connect(
				'activate', self._on_move_clicked, -1
			)
			act.set_enabled(True)
			self.ancestor.get_ancestor(Gtk.Window).get_application().add_action(act)
			item = Gio.MenuItem.new(_('Move up'), 'app.moveup')
			item.set_action_and_target_value('app.moveup', None)
			actions.append_item(item)
			Gio.SimpleAction.new('move-down', None).connect(
				'activate', self._on_move_clicked, 1
			)
			actions.append(_('Move down'), 'move-down')
			if monophony.backend.cache.is_song_being_cached(song['id']):
				pass
			elif monophony.backend.cache.is_song_cached(song['id']):
				Gio.SimpleAction.new('uncache', None).connect(
					'activate', self._on_uncache_clicked
				)
				actions.append(_('Remove from downloads'), 'uncache')
			else:
				Gio.SimpleAction.new('cache', None).connect(
					'activate', self._on_cache_clicked
				)
				actions.append(_('Download to Music folder'), 'cache')
		if player.get_current_song() != song:
			Gio.SimpleAction.new('queue', None).connect(
				'activate', self._on_queue_clicked
			)
			actions.append(_('Add to queue'), 'queue')

		Gio.SimpleAction.new('new-playlist', None).connect(
			'activate', self._on_new_clicked
		)
		actions.append(_('New playlist...'), 'new-playlist')
		# ~ playlists = monophony.backend.playlists.read_playlists()
		# ~ if playlists and song:
			# ~ box_pop.append(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
			# ~ scr_playlists = Gtk.ScrolledWindow.new()
			# ~ scr_playlists.set_max_content_width(80)
			# ~ scr_playlists.set_max_content_height(80)
			# ~ scr_playlists.set_propagate_natural_height(True)
			# ~ scr_playlists.set_policy(
				# ~ Gtk.PolicyType.NEVER,
				# ~ Gtk.PolicyType.AUTOMATIC
			# ~ )
			# ~ box_playlists = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
			# ~ for name, songs in playlists.items():
				# ~ box_playlist = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
				# ~ box_playlist.set_spacing(5)
				# ~ chk_playlist = Gtk.CheckButton.new_with_label(name)
				# ~ chk_playlist.get_last_child().set_max_width_chars(20)
				# ~ chk_playlist.get_last_child().set_ellipsize(
					# ~ Pango.EllipsizeMode.END
				# ~ )
				# ~ chk_playlist.set_active(song['id'] in [s['id'] for s in songs])
				# ~ chk_playlist.connect('toggled', self._on_playlist_toggled, name)
				# ~ box_playlist.append(chk_playlist)
				# ~ box_playlists.append(box_playlist)

			# ~ scr_playlists.set_child(box_playlists)
			# ~ box_pop.append(scr_playlists)

		btn.set_menu_model(self)

	def _on_queue_clicked(self, _b):
		self.popdown()
		if self.song:
			GLib.Thread.new(None, self.player.queue_song, self.song)

	def _on_move_clicked(self, _b, direction: int):
		self.popdown()
		index = self.group['contents'].index(self.song)
		monophony.backend.playlists.swap_songs(
			self.group['title'], index, index + direction
		)

	def _on_uncache_clicked(self, _b):
		self.popdown()
		monophony.backend.cache.uncache_song(self.song['id'])

	def _on_cache_clicked(self, _b):
		self.popdown()
		GLib.Thread.new(
			None, monophony.backend.cache.cache_song, self.song['id']
		)

	def _on_new_clicked(self, _b):
		self.popdown()
		def _create(name: str):
			if self.song:
				monophony.backend.playlists.add_playlist(name, [self.song])
			else:
				monophony.backend.playlists.add_playlist(name)

		MonophonyRenameWindow(self.get_ancestor(Gtk.Window), _create).show()

	def _on_playlist_toggled(self, chk: Gtk.CheckButton, name: str):
		if chk.get_active():
			monophony.backend.playlists.add_song(self.song, name)
		else:
			monophony.backend.playlists.remove_song(self.song['id'], name)
			if self.editable and name == self.group['title']:
				self.popdown()
