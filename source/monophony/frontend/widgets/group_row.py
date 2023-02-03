import monophony.backend.playlists
from monophony.frontend.widgets.song_row import MonophonySongRow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, GLib, Gtk


class MonophonyGroupRow(Adw.ExpanderRow):
	def __init__(self, group: dict, player: object, editable: bool = False):
		super().__init__()

		self.player = player
		self.group = group
		self.editable = editable

		box_pop = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		box_pop.set_spacing(5)
		if editable:
			btn_delete = Gtk.Button.new_with_label(_('Delete'))
			btn_delete.set_has_frame(False)
			btn_delete.connect('clicked', self._on_delete_clicked)
			btn_share = Gtk.Button.new_with_label(_('Export to clipboard'))
			btn_share.set_has_frame(False)
			btn_share.connect('clicked', self._on_share_clicked)
			btn_rename = Gtk.Button.new_with_label(_('Rename...'))
			btn_rename.set_has_frame(False)
			btn_rename.connect('clicked', self._on_rename_clicked)
			box_pop.append(btn_rename)
			box_pop.append(btn_share)
			box_pop.append(btn_delete)
			pop_more = Gtk.Popover.new()
			pop_more.set_child(box_pop)
			btn_more = Gtk.MenuButton()
			btn_more.set_icon_name('view-more')
			btn_more.set_has_frame(False)
			btn_more.set_popover(pop_more)
			btn_more.set_vexpand(False)
			btn_more.set_valign(Gtk.Align.CENTER)
			self.add_prefix(btn_more)

			GLib.timeout_add(100, self.update)

		self.song_widgets = []
		for item in group['contents']:
			row = MonophonySongRow(item, player, group, editable)
			self.add_row(row)
			self.song_widgets.append(row)

		self.set_title(GLib.markup_escape_text(
			group['title'] if 'title' in group else '________',
			-1
		))

	def _on_delete_clicked(self, _b):
		pass

	def _on_share_clicked(self, _b):
		pass

	def _on_rename_clicked(self, _b):
		pass

	def update(self) -> True:
		playlists = monophony.backend.playlists.read_playlists()
		if self.group['title'] not in playlists:
			return True

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
