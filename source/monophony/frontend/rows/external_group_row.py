from monophony.frontend.rows.group_row import MonophonyGroupRow
from monophony.frontend.rows.song_row import MonophonySongRow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


class MonophonyExternalGroupRow(MonophonyGroupRow):
	def __init__(self, group: dict, player: object):
		super().__init__(group, player)

		for item in group['contents']:
			self.add_row(MonophonySongRow(item, player, group))

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
