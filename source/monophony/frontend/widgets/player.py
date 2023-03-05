import monophony.backend.settings
from monophony.frontend.widgets.song_popover import MonophonySongPopover

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gdk, Gio, GLib, Gtk, Pango


class MonophonyPlayer(Gtk.Box):
	def __init__(self, player: object):
		super().__init__(orientation = Gtk.Orientation.VERTICAL)

		self.player = player

		box_title = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		box_title.set_halign(Gtk.Align.START)
		box_title.set_valign(Gtk.Align.CENTER)
		self.spn_loading = Gtk.Spinner.new()
		self.spn_loading.set_halign(Gtk.Align.START)
		self.spn_loading.set_margin_start(10)
		self.spn_loading.set_margin_end(10)
		self.spn_loading.start()
		self.spn_loading.hide()
		box_title.append(self.spn_loading)
		self.lnk_title = Gtk.LinkButton.new_with_label('', '')
		self.lnk_title.set_halign(Gtk.Align.START)
		self.lnk_title.get_child().set_ellipsize(Pango.EllipsizeMode.END)
		box_title.append(self.lnk_title)

		self.btn_pause = Gtk.Button.new_from_icon_name('media-playback-start')
		self.btn_pause.set_valign(Gtk.Align.CENTER)
		self.btn_pause.connect('clicked', self._on_pause_clicked)
		self.btn_pause.set_tooltip_text(_('Toggle pause'))
		self.btn_pause.set_has_frame(False)
		btn_next = Gtk.Button.new_from_icon_name('media-skip-forward')
		btn_next.set_valign(Gtk.Align.CENTER)
		btn_next.set_tooltip_text(_('Next song'))
		btn_next.connect('clicked', self._on_next_clicked)
		btn_next.set_has_frame(False)
		btn_prev = Gtk.Button.new_from_icon_name('media-skip-backward')
		btn_prev.set_valign(Gtk.Align.CENTER)
		btn_prev.set_tooltip_text(_('Previous song'))
		btn_prev.connect('clicked', self._on_previous_clicked)
		btn_prev.set_has_frame(False)
		btn_playlists = Gtk.MenuButton()
		btn_playlists.set_valign(Gtk.Align.CENTER)
		btn_playlists.set_tooltip_text(_('Add to playlist'))
		btn_playlists.set_create_popup_func(MonophonySongPopover, player)
		btn_playlists.set_has_frame(False)
		btn_playlists.set_icon_name('list-add')

		mnu_more = Gio.Menu()
		mnu_more.append(_('Remove From Queue'), 'unqueue-song')
		self.install_action(
			'unqueue-song',
			None,
			lambda p, a, t: p._on_unqueue_clicked()
		)
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
		box_volume.set_margin_start(5)
		box_volume.set_margin_start(5)
		box_volume.set_halign(Gtk.Align.FILL)
		box_volume.set_hexpand(True)
		box_volume.append(lbl_volume)
		box_volume.append(scl_volume)
		itm_volume = Gio.MenuItem()
		itm_volume.set_attribute_value(
			'custom',  GLib.Variant.new_string('volume')
		)
		mnu_more.append_item(itm_volume)
		chk_autoplay = Gtk.CheckButton.new_with_label(_('Radio Mode'))
		chk_autoplay.set_active(
			int(monophony.backend.settings.get_value('radio', False))
		)
		chk_autoplay.connect('toggled', self._on_radio_toggled)
		itm_autoplay = Gio.MenuItem()
		itm_autoplay.set_attribute_value(
			'custom',  GLib.Variant.new_string('autoplay')
		)
		mnu_more.append_item(itm_autoplay)
		chk_loop = Gtk.CheckButton.new_with_label(_('Loop'))
		chk_loop.connect('toggled', self._on_loop_toggled)
		itm_loop = Gio.MenuItem()
		itm_loop.set_attribute_value(
			'custom',  GLib.Variant.new_string('loop')
		)
		mnu_more.append_item(itm_loop)
		chk_shuffle = Gtk.CheckButton.new_with_label(_('Shuffle'))
		chk_shuffle.connect('toggled', self._on_shuffle_toggled)
		itm_shuffle = Gio.MenuItem()
		itm_shuffle.set_attribute_value(
			'custom',  GLib.Variant.new_string('shuffle')
		)
		mnu_more.append_item(itm_shuffle)
		pop_menu = Gtk.PopoverMenu()
		pop_menu.set_menu_model(mnu_more)
		pop_menu.add_child(box_volume, 'volume')
		pop_menu.add_child(chk_autoplay, 'autoplay')
		pop_menu.add_child(chk_loop, 'loop')
		pop_menu.add_child(chk_shuffle, 'shuffle')
		btn_more = Gtk.MenuButton()
		btn_more.set_valign(Gtk.Align.CENTER)
		btn_more.set_icon_name('view-more')
		btn_more.set_tooltip_text(_('More actions'))
		btn_more.set_popover(pop_menu)
		btn_more.set_has_frame(False)

		box_controls = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
		box_controls.set_spacing(2)
		box_controls.set_valign(Gtk.Align.CENTER)
		box_controls.set_halign(Gtk.Align.END)
		box_controls.set_hexpand(True)
		box_controls.append(btn_playlists)
		box_controls.append(btn_prev)
		box_controls.append(self.btn_pause)
		box_controls.append(btn_next)
		box_controls.append(btn_more)

		box_meta = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
		box_meta.set_margin_top(10)
		box_meta.set_margin_bottom(10)
		box_meta.set_margin_start(5)
		box_meta.set_margin_end(5)
		box_meta.set_valign(Gtk.Align.END)
		box_meta.set_halign(Gtk.Align.FILL)
		box_meta.set_hexpand(True)
		box_meta.append(box_title)
		box_meta.append(box_controls)

		self.scl_progress = Gtk.Scale.new_with_range(
			Gtk.Orientation.HORIZONTAL, 0, 1, 0.01
		)
		self.scl_progress.add_css_class('seekbar')
		self.scl_progress.set_draw_value(False)
		self.scl_progress.set_halign(Gtk.Align.FILL)
		self.scl_progress.set_valign(Gtk.Align.END)
		self.scl_progress.connect('change-value', self._on_seek_performed)

		self.set_hexpand(True)
		self.append(self.scl_progress)
		self.append(box_meta)

		css = Gtk.CssProvider.new()
		css.load_from_data('''
			.seekbar {
				padding: 0;
				min-height: 1px;
			}

			.seekbar trough, .seekbar highlight {
				border-radius: 0;
				border-left: none;
				border-right: none;
				min-height: 1px;
			}

			.seekbar highlight {
				border-left: none;
				border-right: none;
			}
		'''.encode())
		Gtk.StyleContext.add_provider_for_display(
			Gdk.Display.get_default(),
			css,
			Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)

		GLib.timeout_add(250, self.update)

	def _on_seek_performed(self, _s, _t, target: float):
		GLib.Thread.new(None, self.player.seek, target)

	def _on_pause_clicked(self, _b):
		self.player.toggle_pause()

	def _on_next_clicked(self, _b):
		GLib.Thread.new(None, self.player.next_song)

	def _on_previous_clicked(self, _b):
		GLib.Thread.new(None, self.player.previous_song)

	def _on_shuffle_toggled(self, btn: Gtk.CheckButton):
		self.player.shuffle = btn.get_active()

	def _on_loop_toggled(self, btn: Gtk.CheckButton):
		self.player.loop = btn.get_active()

	def _on_unqueue_clicked(self):
		self.player.unqueue_song()

	def _on_volume_changed(self, scl: Gtk.Scale):
		self.player.set_volume(scl.get_value())
		monophony.backend.settings.set_value('volume', float(scl.get_value()))

	def _on_radio_toggled(self, chk: Gtk.CheckButton):
		monophony.backend.settings.set_value('radio', int(chk.get_active()))

	def update(self) -> True:
		if self.player.is_busy():
			self.lnk_title.hide()
			if not self.spn_loading.get_visible():
				self.spn_loading.show()
				self.spn_loading.start()
		else:
			self.lnk_title.show()
			self.spn_loading.hide()
			self.scl_progress.set_value(self.player.get_progress())

			if self.player.is_paused():
				self.btn_pause.set_icon_name('media-playback-start')
			else:
				self.btn_pause.set_icon_name('media-playback-pause')

			song = self.player.get_current_song()
			if song:
				self.lnk_title.set_label(song['title'])
				self.lnk_title.set_uri(
					'https://music.youtube.com/watch?v=' + song['id']
				)
			else:
				self.lnk_title.set_label('')
				self.lnk_title.set_uri('')

		return True
