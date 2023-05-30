import monophony.backend.playlists

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gtk, Pango


class MonophonyAddWindow(Adw.Window):
	def __init__(self, song: dict, player):
		super().__init__()

		self.song = song
		self.player = player
		self.add_to_queue = False
		self.add_to_playlists = []

		self.set_title(_('Add to...'))
		self.set_resizable(False)
		self.set_modal(True)

		btn_cancel = Gtk.Button.new_with_label(_('Cancel'))
		btn_cancel.connect('clicked', lambda b: self.destroy())
		btn_add = Gtk.Button.new_with_label(_('Add'))
		btn_add.add_css_class('suggested-action')
		btn_add.connect('clicked', self._on_submit)
		headerbar = Adw.HeaderBar.new()
		headerbar.set_decoration_layout('')
		headerbar.pack_start(btn_cancel)
		headerbar.pack_end(btn_add)

		self.box_list = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		self.box_list.set_spacing(5)
		self.box_list.set_margin_bottom(5)
		self.box_list.set_margin_top(5)
		self.box_list.set_margin_start(5)
		self.box_list.set_margin_end(5)

		scr_list = Gtk.ScrolledWindow.new()
		scr_list.set_min_content_height(200)
		scr_list.set_child(self.box_list)

		ent_name = Gtk.Entry.new()
		ent_name.connect('activate', self._on_create)
		ent_name.set_hexpand(True)
		ent_name.set_halign(Gtk.Align.FILL)
		ent_name.set_placeholder_text(_('New Playlist Name...'))
		btn_create = Gtk.Button.new_with_label(_('Create'))
		btn_create.connect('clicked', lambda b: self._on_create(ent_name))
		box_footer = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
		box_footer.set_spacing(5)
		box_footer.set_margin_bottom(5)
		box_footer.set_margin_top(5)
		box_footer.set_margin_end(5)
		box_footer.set_margin_start(5)
		box_footer.append(ent_name)
		box_footer.append(btn_create)

		box_main = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		box_main.append(headerbar)
		box_main.append(scr_list)
		box_main.append(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
		box_main.append(box_footer)

		self.set_content(box_main)
		self.update_groups()

	def update_groups(self):
		while child := self.box_list.get_first_child():
			self.box_list.remove(child)

		chk_queue = Gtk.CheckButton.new_with_label(_('Queue'))
		for queue_song in self.player.queue:
			if queue_song['id'] == self.song['id']:
				chk_queue.set_active(True)
				chk_queue.set_sensitive(False)
		chk_queue.connect('toggled', self._on_add_to_queue_toggled)
		self.box_list.append(chk_queue)
		self.box_list.append(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
		for playlist, contents in monophony.backend.playlists.read_playlists().items():
			chk_list = Gtk.CheckButton.new()
			lbl_list = Gtk.Label.new(playlist)
			lbl_list.set_ellipsize(Pango.EllipsizeMode.END)
			chk_list.set_child(lbl_list)
			self.box_list.append(chk_list)

			for check_song in contents:
				if check_song['id'] == self.song['id']:
					chk_list.set_active(True)
					chk_list.set_sensitive(False)
					break

			chk_list.connect('toggled', self._on_add_to_playlist_toggled)

	def _on_add_to_queue_toggled(self, btn: Gtk.CheckButton):
		self.add_to_queue = btn.get_active()

	def _on_add_to_playlist_toggled(self, btn: Gtk.CheckButton):
		toggled_list = btn.get_child().get_label()
		if btn.get_active():
			self.add_to_playlists.append(toggled_list)
		else:
			self.add_to_playlists.remove(toggled_list)

	def _on_submit(self, _btn: Gtk.CheckButton):
		for playlist in self.add_to_playlists:
			monophony.backend.playlists.add_song(self.song, playlist)

		if self.add_to_queue:
			self.player.queue_song(self.song)

		self.destroy()

	def _on_create(self, ent: Gtk.Entry):
		text = ent.get_text()
		ent.set_text('')
		if text.strip():
			monophony.backend.playlists.add_playlist(text)
			self.update_groups()
