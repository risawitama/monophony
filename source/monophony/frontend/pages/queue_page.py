from monophony.frontend.rows.queue_song_row import MonophonyQueueSongRow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, GLib, Gtk


class MonophonyQueuePage(Gtk.Box):
	def __init__(self, player: object):
		super().__init__(orientation=Gtk.Orientation.VERTICAL)

		self.player = player
		self.old_queue = []
		self.old_index = -1
		self.queue_widgets = []
		self.set_vexpand(True)

		self.box_meta = Adw.PreferencesPage.new()
		self.box_meta.set_vexpand(True)
		self.box_meta.set_valign(Gtk.Align.FILL)
		self.append(self.box_meta)
		self.box_queue = Adw.PreferencesGroup()
		self.box_queue.set_title(_('Queue'))
		self.box_meta.add(self.box_queue)

		GLib.timeout_add(100, self.update)

	def update(self) -> True:
		new_queue = self.player.queue.copy()
		new_index = self.player.index
		if new_queue != self.old_queue or new_index != self.old_index:
			for widget in self.queue_widgets:
				self.box_queue.remove(widget)

			self.queue_widgets = []
			self.old_queue = new_queue
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

		return True
