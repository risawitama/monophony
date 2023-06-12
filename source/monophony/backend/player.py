import random

import monophony.backend.cache
import monophony.backend.history
import monophony.backend.settings
import monophony.backend.yt

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib, Gst


class PlaybackMode:
	NORMAL = 0
	LOOP = 1
	SHUFFLE = 2
	RADIO = 3


class Player:
	def __init__(self):
		Gst.init([])
		self.lock = GLib.Mutex()
		self.index = 0
		self.queue = []
		self.recent_songs = []
		self.mode = PlaybackMode.NORMAL
		self.error = False
		self.mpris_adapter = None
		self.mpris_server = None
		self.playbin = Gst.ElementFactory.make('playbin', 'playbin')
		self.playbin.set_state(Gst.State.READY)
		self.playbin.set_property('volume', 1)
		self.playbin.set_property('mute', False)

	### --- UTILITY METHODS --- ###
	def terminate(self):
		self.lock.lock()
		self.playbin.set_state(Gst.State.NULL)
		del self.playbin

	def is_busy(self) -> bool:
		if not self.lock.trylock():
			return True

		self.lock.unlock()
		return False

	def is_paused(self) -> bool:
		return self.playbin.get_state(
			Gst.CLOCK_TIME_NONE
		)[1] != Gst.State.PLAYING

	def get_current_song(self) -> dict:
		state = self.playbin.get_state(Gst.CLOCK_TIME_NONE)[1]
		acceptable_states = {Gst.State.PAUSED, Gst.State.PLAYING}

		if len(self.queue) > self.index:
			if state in acceptable_states:
				return self.queue[self.index]

		return {}

	def get_progress(self) -> float:
		duration = self.playbin.query_duration(Gst.Format.TIME)[1]
		position = self.playbin.query_position(Gst.Format.TIME)[1]
		return (position / duration) if duration > 0 else 0.0

	### --- EVENT HANDLERS --- ###

	def _on_bus_error(self, _, err, s_id: str, s_title: str):
		self.lock.lock()
		self.error = True
		self.lock.unlock()

	def _on_song_end(self, *_):
		if self.playbin.get_bus().have_pending():
			return

		GLib.Thread.new(None, self.next_song)

	### --- PLAYBACK CONTROLS --- ###

	def play_song(self, song: dict) -> bool:
		print('Playing', song['id'], 'in playback mode', self.mode)
		if len(self.recent_songs) > 1000:
			self.recent_songs = []
		self.recent_songs.append(song['id'])
		monophony.backend.history.add_song(song)
		self.playbin.set_state(Gst.State.READY)

		uri = monophony.backend.cache.get_song_uri(song['id'])
		if not uri:
			uri = monophony.backend.yt.get_song_uri(song['id'])

		self.playbin.set_property('uri', uri)

		if not uri:
			return False

		bus = self.playbin.get_bus()
		bus.add_signal_watch()
		bus.connect('message::error', self._on_bus_error, song['id'], song['title'])
		bus.connect('message::eos', self._on_song_end)

		self.playbin.set_state(Gst.State.PLAYING)
		if not self.mpris_server._publication_token:
			self.mpris_server.publish()
		self.mpris_adapter.emit_all()
		self.mpris_adapter.on_playback()
		return True

	def play_radio_song(self):
		id_queue = [s['id'] for s in self.queue]
		random.shuffle(id_queue)

		song = None
		for id_ in id_queue:
			song = monophony.backend.yt.get_similar_song(id_, ignore = id_queue)
			if song:
				break

		if song:
			self.queue.append(song)
			self.index += 1
			self.play_song(song)

	def toggle_pause(self):
		state = self.playbin.get_state(Gst.CLOCK_TIME_NONE)[1]

		if state == Gst.State.PLAYING:
			self.playbin.set_state(Gst.State.PAUSED)
		else:
			self.playbin.set_state(Gst.State.PLAYING)

		self.mpris_adapter.on_playpause()

	def next_song(self, ignore_loop: bool = False):
		if not self.lock.trylock():
			return

		while True:
			queue_length = len(self.queue)
			song = None
			if self.mode == PlaybackMode.LOOP and not ignore_loop:
				song = self.queue[self.index]
			elif self.mode == PlaybackMode.SHUFFLE and queue_length > 1:
				for s in self.queue:
					if s['id'] not in self.recent_songs:
						break
				else: # nobreak
					self.recent_songs = []

				song = random.choice([
					s for s in self.queue if s['id'] not in self.recent_songs
				])
				self.index = self.queue.index(song)
			elif queue_length - 1 > self.index :
				self.index += 1
				song = self.queue[self.index]

			if song:
				if self.play_song(song):
					break
				continue

			if self.mode == PlaybackMode.RADIO:
				self.play_radio_song()
			else:
				self.playbin.set_state(Gst.State.NULL)
				self.playbin.set_property('uri', '')
				self.queue = []
				self.index = 0
				self.mpris_server.unpublish()

			break

		self.lock.unlock()

	def previous_song(self):
		if not self.lock.trylock():
			return
		self.playbin.set_state(Gst.State.READY)
		self.index -= 1

		if self.index < 0:
			self.index = 0

		if len(self.queue) > 0:
			song = self.queue[self.index]
			self.play_song(song)

		self.lock.unlock()

	def play_queue(self, queue: list, index: int):
		self.lock.lock()
		if len(queue) == 0:
			self.lock.unlock()
			return

		self.recent_songs = []
		self.queue = queue
		self.index = index
		song = queue[index]
		self.play_song(song)
		self.lock.unlock()

	def unqueue_song(self):
		if not self.queue:
			return

		self.queue.pop(self.index)
		self.index = self.index - 1 if self.index else 0
		if not self.queue:
			self.next_song(True)
			return

		GLib.Thread.new(None, self.play_queue, self.queue, self.index)

	def queue_song(self, song: dict):
		self.lock.lock()
		if not self.queue:
			self.play_song(song)

		self.queue.append(song)
		self.lock.unlock()

	def seek(self, target: float):
		duration = self.playbin.query_duration(Gst.Format.TIME)[1]

		if duration > 0:
			self.playbin.seek_simple(
				Gst.Format.TIME,
				Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
				round(duration * target)
			)
