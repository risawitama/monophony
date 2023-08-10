from monophony.frontend.rows.group_row import MonophonyGroupRow
from monophony.frontend.rows.song_row import MonophonySongRow

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio


class MonophonyImportableGroupRow(MonophonyGroupRow):
	def __init__(self, group: dict, player: object):
		super().__init__(group, player)

		for item in group['contents']:
			self.add_row(MonophonySongRow(item, player, group))

		btn_more = Gtk.MenuButton()
		btn_more.set_tooltip_text(_('More actions'))
		btn_more.set_icon_name('view-more-symbolic')
		btn_more.set_has_frame(False)
		btn_more.set_vexpand(False)
		btn_more.set_valign(Gtk.Align.CENTER)
		btn_more.set_create_popup_func(self._on_show_actions)
		self.add_action(btn_more)

	def _on_show_actions(self, btn: Gtk.MenuButton):
		window = self.get_ancestor(Gtk.Window)
		mnu_actions = Gio.Menu()
		mnu_actions.append(_('Download'), 'cache-playlist')
		window.install_action(
			'cache-playlist',
			None,
			lambda w, *_: w._on_cache_playlist(self.group['contents'])
		)
		mnu_actions.append(_('Import...'), 'import-playlist')
		window.install_action(
			'import-playlist',
			None,
			lambda w, *_: w._on_import_clicked(group=self.group)
		)
		pop_menu = Gtk.PopoverMenu()
		pop_menu.set_menu_model(mnu_actions)
		btn.set_popover(pop_menu)
