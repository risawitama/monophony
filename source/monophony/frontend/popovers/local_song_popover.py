from monophony.frontend.popovers.song_popover import MonophonySongPopover

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


class MonophonyLocalSongPopover(MonophonySongPopover):
	def __init__(self, btn: Gtk.MenuButton, song: dict, parent, group: list):
		super().__init__(btn, song, parent)

		btn.get_ancestor(Gtk.Window).install_action(
			'remove-song',
			None,
			lambda w, *_: w._on_remove_song(song['id'], group['title'])
		)
		self.get_menu_model().append(_('Remove From Playlist'), 'remove-song')

