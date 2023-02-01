import monophony.backend.settings
from monophony.frontend.widgets.song_popover import MonophonySongPopover

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gdk, GLib, Gtk, Pango


class MonophonyPlayer(Gtk.Box):
	def __init__(self, player: object):
		super().__init__(orientation = Gtk.Orientation.VERTICAL)

		self.player = player

		self.spn_loading = Gtk.Spinner.new()
		self.spn_loading.set_halign(Gtk.Align.CENTER)
		self.spn_loading.set_margin_top(10)
		self.spn_loading.set_margin_start(5)
		self.spn_loading.set_margin_end(5)
		self.spn_loading.set_margin_bottom(10)
		self.spn_loading.start()
		self.spn_loading.hide()

		self.lbl_title = Gtk.Label.new('')
		self.lbl_title.set_halign(Gtk.Align.CENTER)
		self.lbl_title.set_ellipsize(Pango.EllipsizeMode.END)
		self.lbl_title.set_margin_top(10)
		self.lbl_title.set_margin_start(5)
		self.lbl_title.set_margin_end(5)
		self.lbl_title.set_margin_bottom(10)

		self.scl_progress = Gtk.Scale.new_with_range(
			Gtk.Orientation.HORIZONTAL, 0, 1, 0.01
		)
		self.scl_progress.set_draw_value(False)
		self.scl_progress.set_halign(Gtk.Align.FILL)
		self.scl_progress.set_valign(Gtk.Align.END)
		self.scl_progress.connect('change-value', self._on_seek_performed)

		self.btn_pause = Gtk.Button.new_from_icon_name('media-playback-start')
		self.btn_pause.connect('clicked', self._on_pause_clicked)
		self.btn_pause.set_has_frame(False)
		btn_next = Gtk.Button.new_from_icon_name('media-skip-forward')
		btn_next.connect('clicked', self._on_next_clicked)
		btn_next.set_has_frame(False)
		btn_prev = Gtk.Button.new_from_icon_name('media-skip-backward')
		btn_prev.connect('clicked', self._on_previous_clicked)
		btn_prev.set_has_frame(False)
		tog_loop = Gtk.ToggleButton()
		tog_loop.set_icon_name('media-playlist-repeat')
		tog_loop.set_has_frame(False)
		tog_loop.connect('toggled', self._on_loop_toggled)
		tog_shuffle = Gtk.ToggleButton()
		tog_shuffle.set_icon_name('media-playlist-shuffle')
		tog_shuffle.set_has_frame(False)
		tog_shuffle.connect('toggled', self._on_shuffle_toggled)
		btn_playlists = Gtk.MenuButton()
		btn_playlists.set_create_popup_func(
			MonophonySongPopover, player, player.get_current_song()
		)
		btn_playlists.set_has_frame(False)
		btn_playlists.set_icon_name('list-add')

		btn_unqueue = Gtk.Button.new_with_label(_('Remove from queue'))
		btn_unqueue.set_has_frame(False)
		btn_unqueue.connect('clicked', self._on_unqueue_clicked)
		btn_url = Gtk.Button.new_with_label(_('Copy song URL'))
		btn_url.set_has_frame(False)
		btn_url.connect('clicked', self._on_copy_clicked)
		lbl_volume = Gtk.Label.new(_('Volume'))
		scl_volume = Gtk.Scale.new_with_range(
			Gtk.Orientation.HORIZONTAL, 0, 1, 0.1
		)
		scl_volume.set_hexpand(True)
		scl_volume.set_value(
			float(monophony.backend.settings.get_value('volume', 1))
		)
		scl_volume.set_draw_value(False)
		scl_volume.connect('value-changed', self._on_volume_changed)
		box_volume = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
		box_volume.set_spacing(5)
		box_volume.set_halign(Gtk.Align.FILL)
		box_volume.set_hexpand(True)
		box_volume.append(lbl_volume)
		box_volume.append(scl_volume)
		chk_autoplay = Gtk.CheckButton.new_with_label(_('Radio mode'))
		chk_autoplay.set_active(
			int(monophony.backend.settings.get_value('radio', False))
		)
		chk_autoplay.get_last_child().set_wrap(True)
		chk_autoplay.connect('toggled', self._on_radio_toggled)
		box_pop = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		box_pop.set_spacing(5)
		box_pop.append(btn_unqueue)
		box_pop.append(btn_url)
		box_pop.append(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
		box_pop.append(box_volume)
		box_pop.append(chk_autoplay)
		self.pop_misc = Gtk.Popover.new()
		self.pop_misc.set_child(box_pop)
		btn_more = Gtk.MenuButton()
		btn_more.set_icon_name('view-more')
		btn_more.set_popover(self.pop_misc)
		btn_more.set_has_frame(False)

		box_controls = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
		box_controls.set_spacing(2)
		box_controls.set_valign(Gtk.Align.END)
		box_controls.set_halign(Gtk.Align.CENTER)
		box_controls.append(btn_playlists)
		box_controls.append(tog_shuffle)
		box_controls.append(btn_prev)
		box_controls.append(self.btn_pause)
		box_controls.append(btn_next)
		box_controls.append(tog_loop)
		box_controls.append(btn_more)

		self.set_hexpand(True)
		self.append(self.spn_loading)
		self.append(self.lbl_title)
		self.append(box_controls)
		self.append(self.scl_progress)

		GLib.timeout_add(100, self.update)

	def _on_seek_performed(self, _s, _t, target: float):
		self.player.seek(target)

	def _on_pause_clicked(self, _b):
		self.player.toggle_pause()

	def _on_next_clicked(self, _b):
		GLib.Thread.new(None, self.player.next_song)

	def _on_previous_clicked(self, _b):
		GLib.Thread.new(None, self.player.previous_song)

	def _on_shuffle_toggled(self, btn: Gtk.ToggleButton):
		self.player.shuffle = btn.get_active()

	def _on_loop_toggled(self, btn: Gtk.ToggleButton):
		self.player.loop = btn.get_active()

	def _on_unqueue_clicked(self, _b):
		self.player.unqueue_song()

	def _on_volume_changed(self, scl: Gtk.Scale):
		self.player.set_volume(scl.get_value())
		monophony.backend.settings.set_value('volume', float(scl.get_value()))

	def _on_copy_clicked(self, _b):
		self.pop_misc.popdown()

		song = self.player.get_current_song()
		if not song:
			return

		self.get_clipboard().set_content(
			Gdk.ContentProvider.new_for_value(
				'https://music.youtube.com/watch?v=' + song['id']
			)
		)

	def _on_radio_toggled(self, chk: Gtk.CheckButton):
		monophony.backend.settings.set_value('radio', int(chk.get_active()))

	def update(self) -> True:
		if self.player.is_busy():
			if not self.spn_loading.get_visible():
				self.spn_loading.show()
				self.spn_loading.start()
			self.lbl_title.hide()
		else:
			self.spn_loading.hide()
			self.lbl_title.show()
			self.scl_progress.set_value(self.player.get_progress())

			if self.player.is_paused():
				self.btn_pause.set_icon_name('media-playback-start')
			else:
				self.btn_pause.set_icon_name('media-playback-pause')

			song = self.player.get_current_song()
			if song:
				self.lbl_title.set_label(song['title'])
			else:
				self.lbl_title.set_label('')

		return True
