from monophony.frontend.popovers.song_popover import MonophonySongPopover

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


class MonophonyQueueSongPopover(MonophonySongPopover):
	def __init__(self, btn: Gtk.MenuButton, song: dict, parent, player: object):
		super().__init__(btn, song, parent)

		self.player = player
		self.install_action(
			'unqueue-song',
			None,
			lambda p, *_: p._on_unqueue_song()
		)
		self.get_menu_model().append(_('Remove From Queue'), 'unqueue-song')

	def _on_unqueue_song(self):
		self.player.unqueue_song(self.song['id'])
