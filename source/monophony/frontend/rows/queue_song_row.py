from monophony.frontend.popovers.queue_song_popover import MonophonyQueueSongPopover
from monophony.frontend.rows.song_row import MonophonySongRow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gdk, Gtk


class MonophonyQueueSongRow(MonophonySongRow):
	def __init__(self, song: dict, player: object, queue: list):
		super().__init__(song, player, queue)
		self.btn_more.set_create_popup_func(
			MonophonyQueueSongPopover, self.song, self.player
		)

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

			.current-queue-item {
				color: @accent_color;
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

	def _on_dnd_drop(self, _t, song_row: Adw.ActionRow, *_) -> bool:
		queue = self.player.queue.copy()
		self.player.move_song(
			queue.index(song_row.song),
			queue.index(self.song),
		)
		return True

	def _on_dnd_prepare(self, *_) -> Gdk.ContentProvider:
		self.add_css_class('dnd-item')
		self.drg_handle.set_icon(Gtk.WidgetPaintable.new(self), 0, 0)
		return Gdk.ContentProvider.new_for_value(self)

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
