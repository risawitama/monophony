import monophony.backend.playlists

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw


class MonophonyDeleteWindow(Adw.MessageDialog):
	def __init__(self, parent: Adw.Window, playlist: str):
		super().__init__()

		self.playlist = playlist

		self.set_heading(_('Delete playlist?'))
		self.add_response('cancel', _('Cancel'))
		self.add_response('delete', _('Delete'))
		self.set_response_appearance(
			'delete', Adw.ResponseAppearance.DESTRUCTIVE
		)
		self.set_transient_for(parent)
		self.set_modal(True)
		self.connect('response', self._on_response)

	def _on_response(self, _w, response: str):
		self.destroy()

		if response == 'delete':
			monophony.backend.playlists.remove_playlist(self.playlist)
