import monophony.backend.playlists
from monophony.frontend.widgets.song_row import MonophonySongRow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gio, GLib, Gtk


class MonophonyGroupRow(Adw.ExpanderRow):
	def __init__(self, group: dict, player: object, editable: bool = False):
		super().__init__()

		self.player = player
		self.group = group
		self.editable = editable

		btn_more = Gtk.MenuButton()
		btn_more.set_icon_name('view-more')
		btn_more.set_has_frame(False)
		btn_more.set_vexpand(False)
		btn_more.set_valign(Gtk.Align.CENTER)
		btn_more.set_create_popup_func(self._on_show_actions)
		self.add_prefix(btn_more)

		if 'author' in self.group:
			self.set_subtitle(GLib.markup_escape_text(self.group['author'], -1))

		self.song_widgets = []
		for item in group['contents']:
			row = MonophonySongRow(item, player, group, editable)
			self.add_row(row)
			self.song_widgets.append(row)

		self.set_title(GLib.markup_escape_text(
			group['title'] if 'title' in group else '________',
			-1
		))

		if self.editable:
			GLib.timeout_add(100, self.update)

	def _on_show_actions(self, btn: Gtk.MenuButton):
		window = self.get_ancestor(Gtk.Window)
		mnu_actions = Gio.Menu()
		if self.editable:
			mnu_actions.append(_('Delete'), 'delete-playlist')
			window.install_action(
				'delete-playlist',
				None,
				lambda w, a, t: w._on_delete_playlist(self)
			)
			mnu_actions.append(_('Rename...'), 'rename-playlist')
			window.install_action(
				'rename-playlist',
				None,
				lambda w, a, t: w._on_rename_playlist(self)
			)
		else:
			mnu_actions.append(_('Save to library'), 'save-playlist')
			window.install_action(
				'save-playlist',
				None,
				lambda w, a, t: w._on_save_playlist(self.group['title'], self.group['contents'])
			)

		btn.set_menu_model(mnu_actions)

	def update(self) -> bool:
		self.set_enable_expansion(self.song_widgets != [])
		playlists = monophony.backend.playlists.read_playlists()
		if self.group['title'] not in playlists:
			self.get_ancestor(Adw.PreferencesGroup).remove(self)
			return False

		if self.group['contents'] == playlists[self.group['title']]:
			return True

		for widget in self.song_widgets:
			self.remove(widget)

		self.song_widgets = []
		self.group['contents'] = playlists[self.group['title']]
		for song in self.group['contents']:
			row = MonophonySongRow(
				song, self.player, self.group, self.editable
			)
			self.add_row(row)
			self.song_widgets.append(row)

		return True
