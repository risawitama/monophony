from monophony.frontend.rows.queue_song_row import MonophonyQueueSongRow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gtk


class MonophonyQueueTab(Gtk.Box):
	def __init__(self, player: object):
		super().__init__(orientation=Gtk.Orientation.VERTICAL)

		self.player = player
		self.player.queue_change_callback = self.update
		self.old_queue = []
		self.old_index = -1
		self.queue_widgets = []
		self.set_vexpand(True)

		self.pge_status = Adw.StatusPage()
		self.pge_status.set_vexpand(True)
		self.pge_status.set_valign(Gtk.Align.FILL)
		self.pge_status.set_icon_name('view-list-symbolic')
		self.pge_status.set_title(_('Queue Empty'))
		self.pge_status.set_visible(True)

		btn_shuffle = Gtk.Button.new_from_icon_name('media-playlist-shuffle-symbolic')
		btn_shuffle.set_tooltip_text(_('Shuffle'))
		btn_shuffle.connect('clicked', lambda _b: self.player.shuffle_queue())

		self.box_queue = Adw.PreferencesGroup()
		self.box_queue.set_header_suffix(btn_shuffle)
		self.box_queue.set_title(_('Queue'))

		self.box_meta = Adw.PreferencesPage.new()
		self.box_meta.set_visible(False)
		self.box_meta.set_vexpand(True)
		self.box_meta.set_valign(Gtk.Align.FILL)
		self.box_meta.add(self.box_queue)

		self.append(self.box_meta)
		self.append(self.pge_status)

	def update(self) -> bool:
		new_queue = self.player.queue.copy()
		new_index = self.player.index

		if new_queue != self.old_queue:
			for widget in self.queue_widgets:
				self.box_queue.remove(widget)

			self.box_meta.set_visible(bool(new_queue))
			self.pge_status.set_visible(not bool(new_queue))

			self.queue_widgets = []
			self.old_queue = new_queue.copy()
			self.old_index = new_index
			for i, song in enumerate(new_queue):
				widget = MonophonyQueueSongRow(
					song,
					self.player,
					{'title': '', 'contents': new_queue}
				)
				if i == new_index:
					widget.add_css_class('current-queue-item')
				self.box_queue.add(widget)
				self.queue_widgets.append(widget)
		elif new_index != self.old_index:
			self.old_index = new_index
			for i, widget in enumerate(self.queue_widgets):
				if i == new_index:
					widget.add_css_class('current-queue-item')
				else:
					widget.remove_css_class('current-queue-item')

		return False
