import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gtk


class MonophonyMessageWindow(Adw.MessageDialog):
	def __init__(self, parent: Adw.Window, title: str, text: str):
		super().__init__()

		self.set_heading(title)
		self.set_body(text)
		self.add_response('ok', _('Ok'))
		self.set_transient_for(parent)
		self.set_modal(True)
		self.connect('response', self._on_response)
		self.add_shortcut(Gtk.Shortcut.new(
			Gtk.ShortcutTrigger.parse_string('Escape'),
			Gtk.CallbackAction.new((lambda w, _: w.close()))
		))

	def _on_response(self, _w, _response: str):
		self.destroy()
