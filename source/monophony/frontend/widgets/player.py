from typing import ClassVar

import monophony.backend.player
import monophony.backend.settings
import monophony.backend.yt

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gdk, Gio, GLib, GObject, Gtk, Pango


class MonophonyPlayer(Gtk.Box):
	playback_icons: ClassVar = {
		monophony.backend.player.PlaybackMode.NORMAL:
		'media-playlist-consecutive-symbolic',
		monophony.backend.player.PlaybackMode.LOOP:
		'media-playlist-repeat-symbolic',
		monophony.backend.player.PlaybackMode.SHUFFLE:
		'media-playlist-shuffle-symbolic',
		monophony.backend.player.PlaybackMode.RADIO:
		'io.gitlab.zehkira.Monophony-symbolic',
	}

	def __init__(self, window: Gtk.Window, player: object):
		super().__init__(orientation=Gtk.Orientation.VERTICAL)
		volume = float(monophony.backend.settings.get_value('volume', 1))

		self.window = window
		self.player = player
		self.player.set_volume(volume, False)
		self.player.ui_update_callback = self.update

		box_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		box_info.set_margin_start(11)
		box_info.set_spacing(5)
		box_info.set_margin_end(5)
		box_info.set_halign(Gtk.Align.START)
		box_info.set_valign(Gtk.Align.CENTER)

		self.lnk_title = Gtk.LinkButton.new_with_label('', '')
		self.lnk_title.set_margin_bottom(2)
		self.lnk_title.set_margin_top(4)

		self.lnk_title.set_halign(Gtk.Align.START)
		self.lnk_title.get_child().set_ellipsize(Pango.EllipsizeMode.END)
		self.lnk_title.add_css_class('title-link')

		self.lbl_author = Gtk.Label(label='')
		self.lbl_author.set_margin_top(2)
		self.lbl_author.set_halign(Gtk.Align.START)
		self.lbl_author.add_css_class('caption')
		self.lbl_author.add_css_class('dim-label')
		self.lbl_author.set_ellipsize(Pango.EllipsizeMode.END)

		self.box_sng_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.box_sng_info.append(self.lnk_title)
		self.box_sng_info.append(self.lbl_author)
		box_info.append(self.box_sng_info)

		self.scl_volume = Gtk.ScaleButton.new(
			0, 1, 0.01,
			[
				'audio-volume-muted-symbolic',
				'audio-volume-high-symbolic',
				'audio-volume-low-symbolic',
				'audio-volume-medium-symbolic',
				'audio-volume-high-symbolic'
			]
		)
		self.scl_volume.set_tooltip_text(_('Volume'))
		popup_volume = self.scl_volume.get_popup()
		box_volume = popup_volume.get_child()
		box_scl_volume = box_volume.get_first_child().get_next_sibling()
		box_scl_volume.set_round_digits(-1)
		self.scl_volume.set_value(volume)
		self.scl_volume.connect('value-changed', self._on_volume_changed)

		self.spn_loading = Gtk.Spinner.new()
		self.spn_loading.set_halign(Gtk.Align.CENTER)
		self.spn_loading.set_margin_start(9)
		self.spn_loading.set_margin_end(9)
		self.spn_loading.set_visible(False)
		self.spn_loading.bind_property(
			'visible',
			self.spn_loading,
			'spinning',
			GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE
		)
		self.btn_pause = Gtk.Button.new_from_icon_name('media-playback-start-symbolic')
		self.btn_pause.set_valign(Gtk.Align.CENTER)
		self.btn_pause.set_tooltip_text(_('Toggle pause'))
		self.btn_pause.set_has_frame(False)
		self.btn_pause.bind_property(
			'visible',
			self.spn_loading,
			'visible',
			GObject.BindingFlags.BIDIRECTIONAL |
			GObject.BindingFlags.SYNC_CREATE |
			GObject.BindingFlags.INVERT_BOOLEAN
		)
		self.btn_pause.connect('clicked', self._on_pause_clicked)
		btn_next = Gtk.Button.new_from_icon_name('media-skip-forward-symbolic')
		btn_next.set_valign(Gtk.Align.CENTER)
		btn_next.set_tooltip_text(_('Next song'))
		btn_next.connect('clicked', self._on_next_clicked)
		btn_next.set_has_frame(False)
		btn_prev = Gtk.Button.new_from_icon_name('media-skip-backward-symbolic')
		btn_prev.set_valign(Gtk.Align.CENTER)
		btn_prev.set_tooltip_text(_('Previous song'))
		btn_prev.connect('clicked', self._on_previous_clicked)
		btn_prev.set_has_frame(False)

		self.btn_mode = Gtk.MenuButton()
		self.btn_mode.set_valign(Gtk.Align.CENTER)
		self.btn_mode.set_icon_name(MonophonyPlayer.playback_icons[player.mode])
		self.btn_mode.set_tooltip_text(_('Playback mode'))
		self.btn_mode.set_create_popup_func(self.build_menu_popup)
		self.btn_mode.set_has_frame(False)

		box_controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		box_controls.set_spacing(2)
		box_controls.set_valign(Gtk.Align.CENTER)
		box_controls.set_halign(Gtk.Align.END)
		box_controls.set_hexpand(True)
		box_controls.append(self.scl_volume)
		box_controls.append(btn_prev)
		box_controls.append(self.btn_pause)
		box_controls.append(self.spn_loading)
		box_controls.append(btn_next)
		box_controls.append(self.btn_mode)

		box_meta = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		box_meta.set_margin_top(10)
		box_meta.set_margin_bottom(10)
		box_meta.set_margin_start(5)
		box_meta.set_margin_end(8)
		box_meta.set_valign(Gtk.Align.END)
		box_meta.set_halign(Gtk.Align.FILL)
		box_meta.set_hexpand(True)
		box_meta.append(box_info)
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
		self.add_css_class('playerbar')

		css = Gtk.CssProvider.new()
		css.load_from_data('''
			.seekbar {
				padding: 0;
				min-height: 10px;
			}

			.seekbar trough, .seekbar highlight {
				border-radius: 0;
				border-left: none;
				border-right: none;
				min-height: 10px;
			}

			.seekbar highlight {
				border-left: none;
				border-right: none;
			}

			.title-link {
				padding-top: 0px;
				padding-bottom: 0px;
				padding-left: 0px;
				padding-right: 0px;
				margin-bottom: -8px;
				margin-top: -8px;
			}

			.playerbar {
				background-color: @headerbar_bg_color;
			}
		''', -1)
		Gtk.StyleContext.add_provider_for_display(
			Gdk.Display.get_default(),
			css,
			Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)

		GLib.timeout_add(1000, self.update_progress)

	def build_menu_popup(self, btn: Gtk.MenuButton):
		mnu_more = Gio.Menu()
		chk_normal = Gtk.CheckButton.new_with_label(_('Normal Playback'))
		chk_normal.set_active(
			self.player.mode == monophony.backend.player.PlaybackMode.NORMAL
		)
		chk_normal.connect('toggled', self._on_normal_toggled)
		itm_normal = Gio.MenuItem()
		itm_normal.set_attribute_value('custom', GLib.Variant.new_string('normal'))
		chk_autoplay = Gtk.CheckButton.new_with_label(_('Radio Mode'))
		chk_autoplay.set_group(chk_normal)
		chk_autoplay.set_active(
			self.player.mode == monophony.backend.player.PlaybackMode.RADIO
		)
		chk_autoplay.connect('toggled', self._on_radio_toggled)
		itm_autoplay = Gio.MenuItem()
		itm_autoplay.set_attribute_value(
			'custom', GLib.Variant.new_string('autoplay')
		)
		chk_loop = Gtk.CheckButton.new_with_label(_('Repeat Song'))
		chk_loop.set_group(chk_normal)
		chk_loop.connect('toggled', self._on_loop_toggled)
		chk_loop.set_active(
			self.player.mode == monophony.backend.player.PlaybackMode.LOOP
		)
		itm_loop = Gio.MenuItem()
		itm_loop.set_attribute_value(
			'custom', GLib.Variant.new_string('loop')
		)
		chk_shuffle = Gtk.CheckButton.new_with_label(_('Shuffle'))
		chk_shuffle.set_group(chk_normal)
		chk_shuffle.set_active(
			self.player.mode == monophony.backend.player.PlaybackMode.SHUFFLE
		)
		chk_shuffle.connect('toggled', self._on_shuffle_toggled)
		itm_shuffle = Gio.MenuItem()
		itm_shuffle.set_attribute_value(
			'custom', GLib.Variant.new_string('shuffle')
		)
		mnu_more.append_item(itm_normal)
		mnu_more.append_item(itm_loop)
		mnu_more.append_item(itm_shuffle)
		mnu_more.append_item(itm_autoplay)
		pop_menu = Gtk.PopoverMenu()
		pop_menu.set_menu_model(mnu_more)
		pop_menu.add_child(chk_normal, 'normal')
		pop_menu.add_child(chk_loop, 'loop')
		pop_menu.add_child(chk_shuffle, 'shuffle')
		pop_menu.add_child(chk_autoplay, 'autoplay')
		btn.set_popover(pop_menu)

	def _on_seek_performed(self, _s, _t, target: float):
		GLib.Thread.new(None, self.player.seek, target)

	def _on_pause_clicked(self, _b):
		self.player.toggle_pause()

	def _on_next_clicked(self, _b):
		GLib.Thread.new(None, self.player.next_song, True)

	def _on_previous_clicked(self, _b):
		GLib.Thread.new(None, self.player.previous_song)

	def _on_shuffle_toggled(self, btn: Gtk.CheckButton):
		if btn.get_active():
			mode = monophony.backend.player.PlaybackMode.SHUFFLE
			self.player.mode = mode
			monophony.backend.settings.set_value('mode', mode)
			self.btn_mode.set_icon_name(
				MonophonyPlayer.playback_icons[self.player.mode]
			)

	def _on_loop_toggled(self, btn: Gtk.CheckButton):
		if btn.get_active():
			mode = monophony.backend.player.PlaybackMode.LOOP
			self.player.mode = mode
			monophony.backend.settings.set_value('mode', mode)
			self.btn_mode.set_icon_name(
				MonophonyPlayer.playback_icons[self.player.mode]
			)

	def _on_normal_toggled(self, btn: Gtk.CheckButton):
		if btn.get_active():
			mode = monophony.backend.player.PlaybackMode.NORMAL
			self.player.mode = mode
			monophony.backend.settings.set_value('mode', mode)
			self.btn_mode.set_icon_name(
				MonophonyPlayer.playback_icons[self.player.mode]
			)

	def _on_radio_toggled(self, btn: Gtk.CheckButton):
		if btn.get_active():
			mode = monophony.backend.player.PlaybackMode.RADIO
			self.player.mode = mode
			monophony.backend.settings.set_value('mode', mode)
			self.btn_mode.set_icon_name(
				MonophonyPlayer.playback_icons[self.player.mode]
			)

	def _on_show_artist_clicked(self):
		song = self.player.get_current_song()
		if song:
			self.window._on_show_artist(song['author_id'])

	def _on_volume_changed(self, _scl, value):
		self.player.set_volume(value, True)
		monophony.backend.settings.set_value('volume', value)

	def update_progress(self) -> bool:
		progress = self.player.get_progress()
		if progress:
			self.scl_progress.set_value(progress)

		return True

	def update(self, song: dict, busy: bool, paused: bool, progress: float) -> bool:
		if song:
			self.lnk_title.set_label(song['title'])
			self.lnk_title.get_child().set_ellipsize(Pango.EllipsizeMode.END)
			self.lnk_title.set_uri(
				'https://music.youtube.com/watch?v=' + song['id']
			)
			self.lbl_author.set_label(song['author'])
			self.window.player_revealer.set_reveal_child(True)
		else:
			self.lnk_title.set_label('')
			self.lnk_title.set_uri('')
			self.lbl_author.set_label('')
			self.window.player_revealer.set_reveal_child(False)

		self.scl_progress.set_sensitive(not busy)
		self.btn_pause.set_visible(not busy)
		self.scl_progress.set_value(progress)
		self.btn_pause.set_icon_name(
			'media-playback-start-symbolic' if paused else
			'media-playback-pause-symbolic'
		)

		return False
