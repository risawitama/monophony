from monophony.backend.player import PlaybackMode

from gi.repository import GLib
from mpris_server.adapters import PlayState, MprisAdapter
from mpris_server.server import Server
from mpris_server.events import EventAdapter


class Adapter(MprisAdapter):
	def __init__(self, monophony_player: object):
		super().__init__()
		self.monophony_player = monophony_player

	def get_uri_schemes(self) -> list:
		return []

	def get_mime_types(self) -> list:
		return []

	def can_quit(self) -> bool:
		return False

	def quit(self):
		pass

	def get_current_position(self) -> float:
		return self.monophony_player.get_progress()

	def next(self):
		GLib.Thread.new(None, self.monophony_player.next_song, True)

	def previous(self):
		GLib.Thread.new(None, self.monophony_player.previous_song)

	def pause(self):
		self.monophony_player.toggle_pause()

	def resume(self):
		self.monophony_player.toggle_pause()

	def stop(self):
		pass

	def play(self):
		pass

	def get_playstate(self) -> PlayState:
		if self.monophony_player.is_paused():
			return PlayState.PAUSED
		return PlayState.PLAYING

	def seek(self, _time):
		return

	def is_repeating(self) -> bool:
		return self.monophony_player.mode == PlaybackMode.LOOP

	def is_playlist(self) -> bool:
		return True

	def set_repeating(self, _val: bool):
		pass

	def set_loop_status(self, _val: str):
		pass

	def get_rate(self) -> float:
		return 1.0

	def set_rate(self, _val: float):
		pass

	def get_shuffle(self) -> bool:
		return self.monophony_player.mode == PlaybackMode.SHUFFLE

	def set_shuffle(self, _val: bool):
		pass

	def get_art_url(self, _track):
		return ''

	def get_volume(self):
		return self.monophony_player.get_volume()

	def set_volume(self, val: float):
		self.monophony_player.set_volume(val, False)

	def get_stream_title(self):
		return ''

	def is_mute(self) -> bool:
		return False

	def set_mute(self, _val: bool):
		pass

	def can_go_next(self) -> bool:
		return True

	def can_go_previous(self) -> bool:
		return True

	def can_play(self) -> bool:
		return bool(self.monophony_player.get_current_song())

	def can_pause(self) -> bool:
		return bool(self.monophony_player.get_current_song())

	def can_seek(self) -> bool:
		return False

	def can_control(self) -> bool:
		return True

	def metadata(self) -> dict:
		song = self.monophony_player.get_current_song()
		if song:
			return {
				'mpris:trackid': '/track/1',
				'mpris:artUrl': song['thumbnail'] if 'thumbnail' in song else '',
				'xesam:title': song['title'] if 'title' in song else '',
				'xesam:artist': [song['author']] if 'author' in song else []
			}

		return {'mpris:trackid': '/org/mpris/MediaPlayer2/TrackList/NoTrack'}


def init(player: object):
	mpris = Server('monophony', adapter = Adapter(player))
	player.mpris_adapter = EventAdapter(root = mpris.root, player = mpris.player)
	player.mpris_server = mpris
	player.mpris_server.loop()
