from monophony.frontend.rows.queue_song_row import MonophonyQueueSongRow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gtk


class MonophonyQueueTab(Gtk.Box):
	def __init__(self, player: object):
		super().__init__(orientation=Gtk.Orientation.VERTICAL)

		player.connect('queue_changed', self._on_queue_changed)
		self.old_queue = []
		self.old_index = -1
		self.queue_widgets = []
		self.set_vexpand(True)

		self.pge_status = Adw.StatusPage()
		self.pge_status.set_vexpand(True)
		self.pge_status.set_valign(Gtk.Align.FILL)
		self.pge_status.set_icon_name('view-list-symbolic')
		self.pge_status.set_title(_('Queue Empty'))
		self.pge_status.set_visible(False)

		self.box_meta = Adw.PreferencesPage.new()
		self.box_meta.set_vexpand(True)
		self.box_meta.set_valign(Gtk.Align.FILL)
		self.box_queue = Adw.PreferencesGroup()
		self.box_meta.add(self.box_queue)

		self.append(self.box_meta)
		self.append(self.pge_status)

	def _on_queue_changed(self, player: object):
		new_queue = player.queue.copy()
		new_index = player.index
		if new_queue != self.old_queue or new_index != self.old_index:
			for widget in self.queue_widgets:
				self.box_queue.remove(widget)

			self.box_meta.set_visible(bool(new_queue))
			self.pge_status.set_visible(not bool(new_queue))

			self.queue_widgets = []
			self.old_queue = new_queue
			self.old_index = new_index
			for i, song in enumerate(new_queue):
				widget = MonophonyQueueSongRow(
					song, player, {'title': '', 'contents': new_queue}
				)
				if i == new_index:
					widget.add_css_class('current-queue-item')
				self.box_queue.add(widget)
				self.queue_widgets.append(widget)
