import monophony.backend.playlists
import monophony.backend.yt
from monophony.frontend.windows.message_window import MonophonyMessageWindow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, GLib, GObject, Gtk


class MonophonyImportWindow(Adw.Window):
	def __init__(self, url: str='', group: list | None = None):
		super().__init__()

		self.import_lock = GLib.Mutex()
		self.error = False
		self.group = group

		self.ent_name = Gtk.Entry.new()
		self.ent_name.set_text(group['title'] if group else '')
		self.ent_name.set_placeholder_text(_('Enter Playlist Name...'))
		self.ent_name.set_hexpand(True)
		self.ent_name.set_margin_start(10)
		self.ent_name.set_margin_end(10)
		self.ent_name.set_halign(Gtk.Align.FILL)
		self.ent_url = Gtk.Entry.new()
		self.ent_url.set_text(url)
		self.ent_url.set_placeholder_text(_('Enter Playlist URL...'))
		self.ent_url.set_hexpand(True)
		self.ent_url.set_halign(Gtk.Align.FILL)
		self.ent_url.set_margin_start(10)
		self.ent_url.set_margin_end(10)
		chk_sync = Gtk.CheckButton.new_with_label(_('Synchronized'))
		self.chk_local = Gtk.CheckButton.new_with_label(_('Editable'))
		self.chk_local.set_group(chk_sync)
		self.chk_local.set_active(True)
		box_type = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		box_type.set_spacing(10)
		box_type.set_margin_start(10)
		box_type.set_margin_end(10)
		box_type.append(self.chk_local)
		box_type.append(chk_sync)

		self.spn_import = Gtk.Spinner.new()
		self.spn_import.set_margin_end(5)
		self.spn_import.set_visible(False)
		self.spn_import.bind_property(
			'visible',
			self.spn_import,
			'spinning',
			GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL
		)
		btn_cancel = Gtk.Button.new_with_label(_('Cancel'))
		btn_cancel.connect('clicked', lambda _b: self.destroy())
		self.btn_import = Gtk.Button.new_with_label(_('Import'))
		self.btn_import.add_css_class('suggested-action')
		self.btn_import.connect('clicked', lambda _b: self._on_submit())
		headerbar = Adw.HeaderBar.new()
		headerbar.set_decoration_layout('')
		headerbar.pack_start(btn_cancel)
		headerbar.pack_end(self.btn_import)
		headerbar.pack_end(self.spn_import)

		self.box_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.box_content.set_spacing(10)
		self.box_content.set_margin_bottom(10)
		self.box_content.append(headerbar)
		self.box_content.append(self.ent_name)
		if not self.group:
			self.box_content.append(self.ent_url)
		self.box_content.append(box_type)

		self.set_title(_('Import playlist...'))
		self.set_modal(True)
		self.set_resizable(False)
		self.set_content(self.box_content)
		self.connect('close-request', lambda w: not w.box_content.get_sensitive())

	def do_import(self, name: str, url: str, local: bool):
		self.import_lock.lock()
		if self.group and local:
			monophony.backend.playlists.add_playlist(name, self.group['contents'])
		elif not monophony.backend.playlists.import_playlist(name, url, local):
			self.error = True
		self.import_lock.unlock()

	def await_import(self) -> bool:
		if self.import_lock.trylock():
			self.import_lock.unlock()
			if self.error:
				self.error = False
				self.box_content.set_sensitive(True)
				self.spn_import.set_visible(False)
				self.btn_import.set_visible(True)
				MonophonyMessageWindow(
					self,
					_('Could not Import Playlist'),
					_('Failed to retrieve playlist data from server.')
				).present()
			else:
				self.destroy()

			return False
		return True

	def _on_submit(self):
		name = self.ent_name.get_text()
		url = (
			'https://www.youtube.com/playlist?list=' + self.group['id']
		) if self.group else self.ent_url.get_text()
		local = self.chk_local.get_active()

		if not name:
			MonophonyMessageWindow(
				self, _('Could not Import Playlist'), _('A name is required.')
			).present()
			return

		if not url and not self.group:
			MonophonyMessageWindow(
				self, _('Could not Import Playlist'), _('A URL is required.')
			).present()
			return

		self.box_content.set_sensitive(False)
		self.spn_import.set_visible(True)
		self.btn_import.set_visible(False)

		GLib.Thread.new(None, self.do_import, name, url, local)
		GLib.timeout_add(1000, self.await_import)
