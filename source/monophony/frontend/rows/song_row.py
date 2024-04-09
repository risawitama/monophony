import monophony.backend.cache
from monophony.frontend.popovers.song_popover import MonophonySongPopover

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, GLib, GObject, Gtk


class MonophonySongRow(Adw.ActionRow, GObject.Object):
	def __init__(self, song: dict, player: object, group: dict | None = None):
		super().__init__()

		self.player = player
		self.song = song
		self.group = group

		self.set_tooltip_text(_('Play'))
		self.set_property('activatable', True)
		self.connect('activated', self._on_play_clicked)

		title = GLib.markup_escape_text(
			song['title'] if song.get('title', None) else '________', -1
		)
		length = GLib.markup_escape_text(
			song['length'], -1
		) if song.get('length', None) else ''
		author = GLib.markup_escape_text(
			song['author'], -1
		) if song.get('author', None) else ''
		subtitle = author
		if length:
			subtitle = length + ' ' + subtitle

		self.checkmark = Gtk.Image.new_from_icon_name('emblem-ok-symbolic')
		self.checkmark.set_tooltip_text(_('Downloaded'))
		self.add_suffix(self.checkmark)
		self.spinner = Gtk.Spinner.new()
		self.spinner.bind_property('visible', self.spinner, 'spinning', 0)
		self.add_suffix(self.spinner)
		self.set_title(title)
		self.set_subtitle(subtitle)

		self.btn_more = Gtk.MenuButton()
		self.btn_more.set_tooltip_text(_('More actions'))
		self.btn_more.set_icon_name('view-more-symbolic')
		self.btn_more.set_has_frame(False)
		self.btn_more.set_vexpand(False)
		self.btn_more.set_valign(Gtk.Align.CENTER)
		self.btn_more.set_create_popup_func(MonophonySongPopover, self.song)
		self.add_suffix(self.btn_more)

		self.update()
		GLib.timeout_add(1000, self.update)

	def _on_play_clicked(self, _b):
		queue = [self.song]
		if self.group:
			queue = self.group['contents']

		GLib.Thread.new(
			None, self.player.play_queue, queue, queue.index(self.song)
		)

	def update(self) -> True:
		self.spinner.set_visible(
			monophony.backend.cache.is_song_being_cached(self.song['id'])
		)
		self.checkmark.set_visible(
			not self.spinner.get_visible() and
			monophony.backend.cache.is_song_cached(self.song['id'])
		)

		return True
