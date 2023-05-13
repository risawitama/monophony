import monophony.backend.cache
import monophony.backend.playlists
from monophony.frontend.widgets.song_popover import MonophonySongPopover

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, GLib, Gtk


class MonophonySongRow(Adw.ActionRow):
	def __init__(self, song: dict, player: object, group: dict = None, editable = False):
		super().__init__()

		self.player = player
		self.song = song
		self.group = group
		self.editable = editable

		btn_play = Gtk.Button.new_from_icon_name('media-playback-start')
		btn_play.set_tooltip_text(_('Play'))
		btn_play.set_vexpand(False)
		btn_play.set_valign(Gtk.Align.CENTER)
		btn_play.connect('clicked', self._on_play_clicked)
		self.add_prefix(btn_play)

		title = GLib.markup_escape_text(
			song['title'] if 'title' in song and song['title'] else '________', -1
		)
		length = GLib.markup_escape_text(
			song['length'], -1
		) if 'length' in song and song['length'] else ''
		author = GLib.markup_escape_text(
			song['author'], -1
		) if 'author' in song and song['author'] else ''
		subtitle = author
		if length:
			subtitle = length + ' ' + subtitle

		self.spinner = Gtk.Spinner.new()
		self.spinner.bind_property('visible', self.spinner, 'spinning', 0)
		self.add_suffix(self.spinner)

		if self.editable:
			btn_more = Gtk.MenuButton()
			btn_more.set_tooltip_text(_('More actions'))
			btn_more.set_create_popup_func(MonophonySongPopover, player, song, group)
			btn_more.set_icon_name('view-more')
			btn_more.set_has_frame(False)
			btn_more.set_vexpand(False)
			btn_more.set_valign(Gtk.Align.CENTER)
			self.add_suffix(btn_more)
		else:
			btn_add_to = Gtk.Button.new_from_icon_name('list-add')
			btn_add_to.set_tooltip_text(_('Add to...'))
			btn_add_to.connect(
				'clicked', lambda b: b.get_ancestor(Gtk.Window)._on_add_clicked(self.song)
			)
			btn_add_to.set_has_frame(False)
			btn_add_to.set_vexpand(False)
			btn_add_to.set_valign(Gtk.Align.CENTER)
			self.add_suffix(btn_add_to)

		self.set_title(title)
		self.set_subtitle(subtitle)

		GLib.timeout_add(100, self.update)

	def _on_play_clicked(self, _b):
		if self.editable:
			queue = monophony.backend.playlists.read_playlists()[
				self.group['title']
			]
		elif self.group:
			queue = self.group['contents']
		else:
			queue = [self.song]

		GLib.Thread.new(
			None, self.player.play_queue, queue, queue.index(self.song)
		)

	def update(self) -> True:
		if self.editable:
			self.spinner.set_visible(monophony.backend.cache.is_song_being_cached(self.song['id']))

		return True
