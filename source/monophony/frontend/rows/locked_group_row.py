from monophony.frontend.rows.group_row import MonophonyGroupRow
from monophony.frontend.rows.song_row import MonophonySongRow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')


class MonophonyLockedGroupRow(MonophonyGroupRow):
	def __init__(self, group: dict, player: object):
		super().__init__(group, player)

		for item in group['contents']:
			self.add_row(MonophonySongRow(item, player, group))
