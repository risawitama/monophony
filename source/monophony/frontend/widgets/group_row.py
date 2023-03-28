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

		if 'author' in self.group:
			self.set_subtitle(GLib.markup_escape_text(self.group['author'], -1))

		self.song_widgets = []
		for item in group['contents']:
			row = MonophonySongRow(item, player, group, editable)
			self.add_row(row)
			self.song_widgets.append(row)

		self.set_title(GLib.markup_escape_text(
			group['title'] if 'title' in group and group['title'] else '________',
			-1
		))

		btn_play = Gtk.Button.new_from_icon_name('media-playback-start')
		btn_play.set_tooltip_text(_('Play'))
		btn_play.set_vexpand(False)
		btn_play.set_valign(Gtk.Align.CENTER)
		btn_play.connect('clicked', self._on_play_clicked)
		self.add_prefix(btn_play)

		if self.editable:
			btn_more = Gtk.MenuButton()
			btn_more.set_tooltip_text(_('More actions'))
			btn_more.set_icon_name('view-more')
			btn_more.set_has_frame(False)
			btn_more.set_vexpand(False)
			btn_more.set_valign(Gtk.Align.CENTER)
			btn_more.set_create_popup_func(self._on_show_actions)
			self.add_action(btn_more)

			GLib.timeout_add(100, self.update)
		else:
			btn_save = Gtk.Button.new_from_icon_name('list-add-symbolic')
			btn_save.set_tooltip_text(_('Add to library'))
			btn_save.set_vexpand(False)
			btn_save.set_valign(Gtk.Align.CENTER)
			btn_save.set_has_frame(False)
			btn_save.connect(
				'clicked',
				lambda b, t, c: b.get_ancestor(Gtk.Window)._on_save_playlist(t, c),
				self.group['title'],
				self.group['contents']
			)
			self.add_action(btn_save)

	def _on_play_clicked(self, _b):
		if self.editable:
			queue = monophony.backend.playlists.read_playlists()[
				self.group['title']
			]
		elif self.group:
			queue = self.group['contents']
		else:
			return

		GLib.Thread.new(None, self.player.play_queue, queue, 0)

	def _on_show_actions(self, btn: Gtk.MenuButton):
		window = self.get_ancestor(Gtk.Window)
		mnu_actions = Gio.Menu()
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
