import monophony.backend.playlists

from monophony.frontend.rows.group_row import MonophonyGroupRow
from monophony.frontend.rows.song_row import MonophonySongRow
from monophony.frontend.windows.message_window import MonophonyMessageWindow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gtk, Gio


class MonophonyExternalGroupRow(MonophonyGroupRow):
	def __init__(self, group: dict, player: object):
		super().__init__(group, player)

		self.song_widgets = []
		for song in self.group['contents']:
			row = MonophonySongRow(song, self.player, self.group)
			self.add_row(row)
			self.song_widgets.append(row)

		btn_more = Gtk.MenuButton()
		btn_more.set_tooltip_text(_('More actions'))
		btn_more.set_icon_name('view-more-symbolic')
		btn_more.set_has_frame(False)
		btn_more.set_vexpand(False)
		btn_more.set_valign(Gtk.Align.CENTER)
		btn_more.set_create_popup_func(self._on_show_actions)
		self.add_action(btn_more)
		self.set_subtitle(_('Synchronized'))

		playlists = monophony.backend.playlists.read_external_playlists()
		for playlist in playlists:
			if playlist['title'] == self.group['title']:
				self.group['contents'] = playlist['contents']
				break
		for song in self.group['contents']:
			self.add_row(MonophonySongRow(song, self.player, self.group))
		self.set_enable_expansion(self.song_widgets != [])

	def _on_show_actions(self, btn: Gtk.MenuButton):
		window = self.get_ancestor(Gtk.Window)
		mnu_actions = Gio.Menu()
		mnu_actions.append(_('Delete'), 'delete-playlist')
		window.install_action(
			'delete-playlist', None, lambda *_: self._on_delete()
		)
		mnu_actions.append(_('Download'), 'cache-playlist')
		window.install_action(
			'cache-playlist',
			None,
			lambda w, *_: w._on_cache_playlist(self.group['contents'])
		)
		mnu_actions.append(_('Rename...'), 'rename-playlist')
		window.install_action(
			'rename-playlist',
			None,
			lambda *_: self._on_open_rename_menu(btn)
		)
		pop_menu = Gtk.PopoverMenu()
		pop_menu.set_menu_model(mnu_actions)
		btn.set_popover(pop_menu)

	def _on_open_rename_menu(self, btn: Gtk.MenuButton):
		pop_rename = Gtk.Popover.new()
		ent_name = Gtk.Entry.new()
		ent_name.set_text(self.group['title'])
		ent_name.connect(
			'activate', lambda e: self._on_rename(e.get_text(), pop_rename)
		)
		btn_rename = Gtk.Button.new_with_label(_('Rename'))
		btn_rename.add_css_class('suggested-action')
		btn_rename.connect(
			'clicked', lambda _b: self._on_rename(ent_name.get_text(), pop_rename)
		)
		box_rename = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		box_rename.set_spacing(5)
		box_rename.set_margin_top(5)
		box_rename.set_margin_bottom(5)
		box_rename.set_margin_start(5)
		box_rename.set_margin_end(5)
		box_rename.append(ent_name)
		box_rename.append(btn_rename)
		pop_rename.set_child(box_rename)
		pop_rename.set_parent(btn)
		btn.popdown()
		pop_rename.popup()

	def _on_delete(self):
		self.get_ancestor(Gtk.Window)._on_delete_playlist(self, local=False)
		self.get_ancestor(Adw.PreferencesGroup).remove(self)

	def _on_rename(self, name: str, pop: Gtk.Popover):
		pop.popdown()
		success = monophony.backend.playlists.rename_playlist(
			self.group['title'], name, False
		)
		if success:
			self.group['title'] = name
			self.set_title(name)
		else:
			MonophonyMessageWindow(
				self.get_ancestor(Gtk.Window),
				_('Could not Rename'),
				_('Playlist already exists')
			).present()

