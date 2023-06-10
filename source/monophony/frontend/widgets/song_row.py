import monophony.backend.cache
import monophony.backend.playlists
from monophony.frontend.widgets.song_popover import MonophonySongPopover

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gdk, GLib, GObject, Gtk


class MonophonySongRow(Adw.ActionRow, GObject.Object):
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

		if self.editable and self.group:
			img_handle = Gtk.Image.new_from_icon_name('list-drag-handle-symbolic')
			img_handle.add_css_class('drag-handle')
			css = Gtk.CssProvider.new()
			css.load_from_data('''
				.drag-handle {
					opacity: 0.5;
				}

				.dnd-item {
					background-color: #00000022;
				}
			''', -1)
			Gtk.StyleContext.add_provider_for_display(
				Gdk.Display.get_default(),
				css,
				Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
			)
			self.add_prefix(img_handle)
			self.drg_handle = Gtk.DragSource.new()
			self.drg_handle.set_actions(Gdk.DragAction.MOVE)
			self.drg_handle.connect('prepare', self._on_dnd_prepare)
			self.drg_handle.connect('drag-end', self._on_dnd_cancel_or_end)
			self.drg_handle.connect('drag-cancel', self._on_dnd_cancel_or_end)
			img_handle.add_controller(self.drg_handle)
			self.drp_target = Gtk.DropTarget.new(self.__gtype__, Gdk.DragAction.MOVE)
			self.drp_target.connect('drop', self._on_dnd_drop)
			self.drp_target.connect('enter', self._on_dnd_enter)
			self.add_controller(self.drp_target)
			btn_more = Gtk.MenuButton()
			btn_more.set_tooltip_text(_('More actions'))
			btn_more.set_create_popup_func(MonophonySongPopover, player, song, group)
			btn_more.set_icon_name('view-more')
			btn_more.set_has_frame(False)
			btn_more.set_vexpand(False)
			btn_more.set_valign(Gtk.Align.CENTER)
			self.add_suffix(btn_more)

			GLib.timeout_add(1000, self.update)
		else:
			btn_add_to = Gtk.Button.new_from_icon_name('list-add')
			btn_add_to.set_tooltip_text(_('Add to...'))
			btn_add_to.connect(
				'clicked',
				lambda b: b.get_ancestor(Gtk.Window)._on_add_clicked(self.song)
			)
			btn_add_to.set_has_frame(False)
			btn_add_to.set_vexpand(False)
			btn_add_to.set_valign(Gtk.Align.CENTER)
			self.add_suffix(btn_add_to)

		self.set_title(title)
		self.set_subtitle(subtitle)

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

	def _on_dnd_prepare(self, *_) -> Gdk.ContentProvider:
		self.add_css_class('dnd-item')
		self.drg_handle.set_icon(Gtk.WidgetPaintable.new(self), 0, 0)
		return Gdk.ContentProvider.new_for_value(self)

	def _on_dnd_drop(self, _t, song_row: Adw.ActionRow, x: float, y: float) -> bool:
		monophony.backend.playlists.move_song(
			self.group['title'],
			self.group['contents'].index(song_row.song),
			self.group['contents'].index(self.song),
		)
		return True

	def _on_dnd_enter(self, *_) -> int:
		if self.drg_handle.get_drag():
			self.drp_target.reject()
			return 0

		# reject if no drag was started in the local group
		child_index = 0
		while True:
			child = self.get_parent().get_row_at_index(child_index)
			child_index += 1
			if not child:
				self.drp_target.reject()
				return 0
			if child.drg_handle.get_drag():
				return Gdk.DragAction.MOVE

	def _on_dnd_cancel_or_end(self, *_):
		self.remove_css_class('dnd-item')

	def update(self) -> True:
		if self.editable:
			self.spinner.set_visible(
				monophony.backend.cache.is_song_being_cached(self.song['id'])
			)

		return True
