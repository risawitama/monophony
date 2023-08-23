import random

import monophony.backend.cache
import monophony.backend.history
import monophony.backend.settings
import monophony.backend.yt

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstAudio', '1.0')
from gi.repository import GLib, Gst, GstAudio


class PlaybackMode:
	NORMAL = 0
	LOOP = 1
	SHUFFLE = 2
	RADIO = 3


class Player:
	def __init__(self):
		Gst.init([])
		self.lock = GLib.Mutex()
		self.interrupt = False
		self.index = 0
		self.queue = []
		self.recent_songs = []
		self.last_progress = 0
		self.mode = PlaybackMode.NORMAL
		self.mpris_adapter = None
		self.mpris_server = None
		self.playbin = Gst.ElementFactory.make('playbin', 'playbin')
		self.playbin.set_state(Gst.State.READY)
		self.playbin.get_bus().add_signal_watch()
		self.playbin.get_bus().connect('message::error', self._on_bus_error)
		self.playbin.get_bus().connect('message::stream-start', self._on_song_start)
		self.playbin.get_bus().connect('message::eos', self._on_song_end)

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

	def get_current_song(self, lock: bool=True) -> dict:
		if lock and not self.lock.trylock():
			try:
				return self.queue[self.index]
			except IndexError:
				return {}

		state = self.playbin.get_state(Gst.CLOCK_TIME_NONE)[1]
		acceptable_states = {Gst.State.PAUSED, Gst.State.PLAYING}
		result = {}

		if state in acceptable_states:
			try:
				result = self.queue[self.index]
			except IndexError:
				pass

		if lock:
			self.lock.unlock()
		return result

	def get_progress(self) -> float:
		duration = self.playbin.query_duration(Gst.Format.TIME)[1]
		position = self.playbin.query_position(Gst.Format.TIME)[1]
		return (position / duration) if duration > 0 else 0.0

	def set_volume(self, volume_cubic: float, notify_mpris: bool):
		self.lock.lock()
		volume_linear = self.playbin.convert_volume(
			GstAudio.StreamVolumeFormat.CUBIC,
			GstAudio.StreamVolumeFormat.LINEAR,
			volume_cubic
		)
		self.playbin.set_property('volume', volume_linear)
		self.lock.unlock()
		if notify_mpris:
			self.mpris_adapter.on_volume()

	def get_volume(self) -> float:
		return self.playbin.convert_volume(
			GstAudio.StreamVolumeFormat.LINEAR,
			GstAudio.StreamVolumeFormat.CUBIC,
			self.playbin.get_property('volume')
		)

	### --- EVENT HANDLERS --- ###

	def _on_bus_error(self, _, err):
		print('Playback error:', err.parse_error().gerror.message)
		self.last_progress = self.playbin.query_position(Gst.Format.TIME)[1]
		GLib.Thread.new(
			None,
			self.play_song,
			self.queue[self.index],
			True,
			True
		)

	def _on_song_start(self, _bus, _msg):
		self.lock.lock()

		if self.last_progress >= 0:
			print('Seeking to', self.last_progress)
			self.playbin.seek_simple(
				Gst.Format.TIME,
				Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT | Gst.SeekFlags.ACCURATE,
				self.last_progress
			)

		self.last_progress = 0
		self.lock.unlock()

	def _on_song_end(self, *_):
		if self.playbin.get_bus().have_pending():
			return

		GLib.Thread.new(None, self.next_song)

	### --- PLAYBACK CONTROLS --- ###

	def play_song(self, song: dict, lock: bool=False, resume: bool=False):
		if lock:
			self.lock.lock()

		if not resume:
			print('Playing', song['id'], 'in playback mode', self.mode)
			self.last_progress = 0
		else:
			print('Resuming', song['id'], 'in playback mode', self.mode)

		if song['id'] not in self.recent_songs:
			self.recent_songs.append(song['id'])
		monophony.backend.history.add_song(song)
		self.playbin.set_state(Gst.State.READY)

		uri = monophony.backend.cache.get_song_uri(song['id'])
		if not uri:
			while True:
				uri = monophony.backend.yt.get_song_uri(song['id'])
				if uri is not None:
					break
				if self.interrupt:
					if lock:
						self.lock.unlock()
					return

		self.playbin.set_property('uri', uri)
		self.playbin.set_state(Gst.State.PLAYING)
		self.mpris_server.unpublish()
		self.mpris_server.publish()
		self.mpris_adapter.emit_all()
		self.mpris_adapter.on_playback()

		if lock:
			self.lock.unlock()

	def play_radio_song(self):
		id_queue = [s['id'] for s in self.queue]
		random.shuffle(id_queue)

		song = None
		for id_ in id_queue:
			song = monophony.backend.yt.get_similar_song(id_, ignore=id_queue)
			if song and song['id']:
				break

		if song:
			self.queue.append(song)
			self.index += 1
			self.play_song(song)

	def toggle_pause(self):
		if not self.lock.trylock():
			return

		state = self.playbin.get_state(Gst.CLOCK_TIME_NONE)[1]
		if state == Gst.State.PLAYING:
			self.playbin.set_state(Gst.State.PAUSED)
		else:
			self.playbin.set_state(Gst.State.PLAYING)

		self.mpris_adapter.on_playpause()
		self.lock.unlock()

	def next_song(self, ignore_loop: bool=False, lock: bool=True):
		if lock and not self.lock.trylock():
			return

		queue_length = len(self.queue)
		song = None
		if self.mode == PlaybackMode.LOOP and not ignore_loop:
			song = self.queue[self.index]
		elif self.mode == PlaybackMode.SHUFFLE and queue_length > 1:
			for s in self.queue:
				if s['id'] not in self.recent_songs:
					break
			else: # nobreak
				if self.recent_songs:
					self.recent_songs = [self.recent_songs[-1]]

			song = random.choice([
				s for s in self.queue if s['id'] not in self.recent_songs
			])
			self.index = self.queue.index(song)
		elif queue_length - 1 > self.index :
			self.index += 1
			song = self.queue[self.index]

		if song:
			self.play_song(song)
		elif self.mode == PlaybackMode.RADIO:
			self.play_radio_song()
		else:
			self.playbin.set_state(Gst.State.NULL)
			self.playbin.set_property('uri', '')
			self.queue = []
			self.index = 0
			self.mpris_server.unpublish()

		if lock:
			self.lock.unlock()

	def previous_song(self):
		if not self.lock.trylock():
			return
		self.playbin.set_state(Gst.State.READY)

		self.index = max(self.index - 1, 0)
		if len(self.recent_songs) > 1:
			recent = self.recent_songs[-2]
			for i, queue_song in enumerate(self.queue):
				if queue_song['id'] == recent:
					self.index = i
					self.recent_songs.pop(-1)
					break

		if len(self.queue) > 0:
			song = self.queue[self.index]
			self.play_song(song)

		self.lock.unlock()

	def play_queue(self, queue: list, index: int):
		if not self.lock.trylock():
			self.interrupt = True
			self.lock.lock()
			self.interrupt = False

		if len(queue) == 0:
			self.lock.unlock()
			return

		self.recent_songs = []
		self.queue = queue
		self.index = index
		song = queue[index]
		self.play_song(song)
		self.lock.unlock()

	def unqueue_song(self, song_id: str):
		self.lock.lock()
		if not self.queue:
			self.lock.unlock()
			return

		for i, song in enumerate(self.queue):
			if song['id'] == song_id:
				old_index = self.index
				self.queue.pop(i)
				if old_index < i:
					break
				self.index -= 1
				if old_index == i:
					self.next_song(True, lock=False)
				break

		self.lock.unlock()

	def move_song(self, from_i: int, to_i: int):
		if not self.lock.trylock():
			return

		to_song = self.queue[to_i]
		from_song = self.queue.pop(from_i)
		self.queue.insert(self.queue.index(to_song), from_song)
		if from_i == self.index:
			if to_i > self.index:
				self.index = to_i - 1
			else:
				self.index = to_i
		elif from_i < self.index and to_i > self.index:
			self.index -= 1
		elif from_i > self.index and to_i <= self.index:
			self.index += 1

		self.lock.unlock()

	def queue_song(self, song: dict):
		if not self.lock.trylock():
			return

		if not self.queue:
			self.play_song(song)

		self.queue.append(song)
		self.lock.unlock()

	def seek(self, target: float):
		if not self.lock.trylock():
			return

		duration = self.playbin.query_duration(Gst.Format.TIME)[1]
		if duration > 0 and self.get_current_song(lock=False):
			self.playbin.seek_simple(
				Gst.Format.TIME,
				Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
				round(duration * target)
			)

		self.lock.unlock()
