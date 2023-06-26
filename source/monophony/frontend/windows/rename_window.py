import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gtk


class MonophonyRenameWindow(Adw.MessageDialog):
	def __init__(self, parent: Adw.Window, callback: callable, name: str = ''):
		super().__init__()

		self.callback = callback

		entry = Gtk.Entry.new()
		entry.set_text(name)
		entry.set_placeholder_text(_('Enter new Name...'))
		entry.connect('activate', lambda _e: self.response('ok'))

		self.add_response('cancel', _('Cancel'))
		self.add_response('ok', _('Rename'))
		self.set_response_appearance('ok', Adw.ResponseAppearance.SUGGESTED)
		self.set_heading(_('Rename Playlist'))
		self.set_transient_for(parent)
		self.set_modal(True)
		self.set_resizable(False)
		self.set_extra_child(entry)
		self.connect('response', self._on_response)

	def _on_response(self, _w, response: str):
		if response == 'ok':
			name = self.get_extra_child().get_text()
			if name:
				self.callback(name)

		self.destroy()
