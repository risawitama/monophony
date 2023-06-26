import monophony.backend.playlists

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, GLib, Gtk


class MonophonyAddWindow(Adw.Window):
	def __init__(self, song: dict, player):
		super().__init__()

		self.song = song
		self.player = player
		self.add_to_queue = False
		self.add_to_playlists = []
		self.playlists = []

		self.set_title(_('Add to...'))
		self.set_default_size(400, 600)
		self.set_property('width-request', 360)
		self.set_property('height-request', 360)
		self.set_modal(True)

		btn_cancel = Gtk.Button.new_with_label(_('Cancel'))
		btn_cancel.connect('clicked', lambda _b: self.destroy())
		btn_add = Gtk.Button.new_with_label(_('Add'))
		btn_add.add_css_class('suggested-action')
		btn_add.connect('clicked', self._on_submit)
		headerbar = Adw.HeaderBar.new()
		headerbar.set_decoration_layout('')
		headerbar.pack_start(btn_cancel)
		headerbar.pack_end(btn_add)

		grp_queue = Adw.PreferencesGroup()
		self.chk_queue = Gtk.CheckButton()
		self.row_queue = Adw.ActionRow()
		self.row_queue.add_suffix(self.chk_queue)
		self.row_queue.set_title(_('Queue'))
		self.row_queue.set_property('activatable-widget', self.chk_queue)
		self.chk_queue.connect('toggled', self._on_add_to_queue_toggled)
		grp_queue.add(self.row_queue)

		self.grp_list = Adw.PreferencesGroup()
		self.grp_list.set_title(_('Your Playlists'))

		ent_name = Gtk.Entry.new()
		ent_name.connect('activate', self._on_create)
		ent_name.set_hexpand(True)
		ent_name.set_halign(Gtk.Align.FILL)
		ent_name.set_placeholder_text(_('New Playlist Name...'))

		btn_create = Gtk.Button.new_with_label(_('Create'))
		btn_create.connect('clicked', lambda _b: self._on_create(ent_name))

		box_create = Gtk.Box()
		box_create.set_spacing(5)
		box_create.set_hexpand(True)
		box_create.append(ent_name)
		box_create.append(btn_create)

		clamp_create = Adw.Clamp()
		clamp_create.set_maximum_size(576)
		clamp_create.set_hexpand(True)
		clamp_create.set_child(box_create)

		bar_name = Gtk.ActionBar()
		bar_name.set_center_widget(clamp_create)

		page_list = Adw.PreferencesPage()
		page_list.set_vexpand(True)
		page_list.add(grp_queue)
		page_list.add(self.grp_list)

		box_main = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		box_main.append(headerbar)
		box_main.append(page_list)
		box_main.append(bar_name)

		self.set_content(box_main)
		self.update_groups()

	def update_groups(self):
		for child in self.playlists:
			self.grp_list.remove(child)

		self.playlists.clear()

		for queue_song in self.player.queue:
			if queue_song['id'] == self.song['id']:
				self.chk_queue.set_active(True)
				self.chk_queue.set_sensitive(False)
				self.row_queue.set_sensitive(False)
			else:
				self.chk_queue.set_active(False)
				self.chk_queue.set_sensitive(True)
				self.row_queue.set_sensitive(True)

		for playlist, contents in monophony.backend.playlists.read_playlists().items():
			chk_list = Gtk.CheckButton.new()
			row_list = Adw.ActionRow()
			row_list.add_suffix(chk_list)
			row_list.set_title(playlist)
			row_list.set_property('activatable-widget', chk_list)
			self.grp_list.add(row_list)
			self.playlists.append(row_list)

			for check_song in contents:
				if check_song['id'] == self.song['id']:
					chk_list.set_active(True)
					chk_list.set_sensitive(False)
					row_list.set_sensitive(False)
					break

			chk_list.connect('toggled', self._on_add_to_playlist_toggled)

	def _on_add_to_queue_toggled(self, btn: Gtk.CheckButton):
		self.add_to_queue = btn.get_active()

	def _on_add_to_playlist_toggled(self, btn: Gtk.CheckButton):
		toggled_list = btn.get_parent().get_parent().get_parent().get_title()
		if btn.get_active():
			self.add_to_playlists.append(toggled_list)
		else:
			self.add_to_playlists.remove(toggled_list)

	def _on_submit(self, _btn: Gtk.CheckButton):
		for playlist in self.add_to_playlists:
			monophony.backend.playlists.add_song(self.song, playlist)

		if self.add_to_queue:
			GLib.Thread.new(None, self.player.queue_song, self.song)

		self.destroy()

	def _on_create(self, ent: Gtk.Entry):
		text = ent.get_text()
		ent.set_text('')

		if text.strip():
			monophony.backend.playlists.add_playlist(text)
			self.update_groups()
