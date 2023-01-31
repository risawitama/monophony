import random, time

import monophony.backend.cache
import monophony.backend.settings
import monophony.backend.sponsorblock
import monophony.backend.yt

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib, Gst


class Player:
	def __init__(self):
		self.playbin: Gst.Element = None
		self.playbin_lock = GLib.Mutex()
		self.index: int = 0
		self.skip_segments: dict = {}
		self.queue: list = []
		self.loop: bool = False
		self.shuffle: bool = False
		self.playback_retries: int = 0
		self.error: bool = False

		Gst.init([])
		self._remake_playbin()

	### --- UTILITY METHODS --- ###

	def _remake_playbin(self):
		if self.playbin:
			self.playbin.set_state(Gst.State.NULL)
			del self.playbin

		self.playbin = Gst.ElementFactory.make('playbin', 'playbin')
		self.playbin.set_state(Gst.State.READY)
		self.playbin.set_property(
			'volume', float(monophony.backend.settings.get_value('volume', 1))
		)
		self.playbin.set_property('mute', False)

	def terminate(self):
		self.playbin_lock.lock()
		self.playbin.set_state(Gst.State.NULL)
		del self.playbin

	def is_busy(self) -> bool:
		if not self.playbin_lock.trylock():
			return True

		self.playbin_lock.unlock()
		return False

	def is_paused(self) -> bool:
		return self.playbin.get_state(
			Gst.CLOCK_TIME_NONE
		)[1] != Gst.State.PLAYING

	def get_current_song(self) -> dict:
		state = self.playbin.get_state(Gst.CLOCK_TIME_NONE)[1]
		acceptable_states = {Gst.State.PAUSED, Gst.State.PLAYING}

		if len(self.queue) > self.index and state in acceptable_states:
			return self.queue[self.index]

		return {}

	def get_progress(self) -> float:
		while not self.playbin_lock.trylock():
			pass

		duration = self.playbin.query_duration(Gst.Format.TIME)[1]
		position = self.playbin.query_position(Gst.Format.TIME)[1]

		self.playbin_lock.unlock()
		return (position / duration) if duration > 0 else 0.0

	### --- EVENT HANDLERS --- ###

	def _on_auto_skip(self) -> True:
		# low priority
		if not self.playbin_lock.trylock():
			return True

		duration = self.playbin.query_duration(Gst.Format.TIME)[1]
		position = self.playbin.query_position(Gst.Format.TIME)[1]

		if duration > 0:
			pos_seconds = position / Gst.SECOND
			for start, end in self.skip_segments.items():
				if pos_seconds >= start and pos_seconds < end:
					self.playbin.seek_simple(
						Gst.Format.TIME,
						Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE,
						end * Gst.SECOND
					)
					break

		self.playbin_lock.unlock()
		return True

	def _on_bus_error(self, _, err, s_id: str, s_title: str):
		self._remake_playbin()

		# wait before retrying - if it's 403 yt might block again
		time.sleep(2)
		if self.playback_retries > 1:
			self.error = True
			return

		self.playback_retries += 1
		self.play_song(s_id, s_title)

	def _on_song_end(self, *_):
		if self.playbin.get_bus().have_pending():
			return

		self.playback_retries = 0
		self._remake_playbin()

		song = None
		queue_length = len(self.queue)
		if self.loop:
			song = self.queue[self.index]
		elif self.shuffle and queue_length > 1:
			random_index = self.index
			while random_index == self.index:
				random_index = random.randrange(0, queue_length)

			self.index = random_index
			song = self.queue[self.index]
		elif queue_length - 1 > self.index:
			self.index += 1
			song = self.queue[self.index]

		if song:
			GLib.Thread.new(None, self.play_song, song['id'], song['title'])
			return

		GLib.Thread.new(None, self.play_radio_song)

	### --- PLAYBACK CONTROLS --- ###

	def play_song(self, id_: str, title: str):
		self.playbin_lock.lock()
		self._remake_playbin()
		self.playbin.set_state(Gst.State.READY)

		uri = monophony.backend.cache.get_song_uri(id_)
		if not uri:
			uri = monophony.backend.yt.get_song_uri(id_)

		self.playbin.set_property('uri', uri)

		if not uri:
			self.playbin_lock.unlock()
			self.error = True
			return

		if not monophony.backend.cache.is_song_cached(id_):
			self.skip_segments = monophony.backend.sponsorblock.get_segments(
				id_
			)

		bus = self.playbin.get_bus()
		bus.add_signal_watch()
		bus.connect('message::error', self._on_bus_error, id_, title)
		bus.connect('message::eos', self._on_song_end)

		self.playbin.set_state(Gst.State.PLAYING)
		self.playbin_lock.unlock()
		return

	def play_radio_song(self):
		if not int(monophony.backend.settings.get_value('radio', 0)):
			return

		id_queue = [s['id'] for s in self.queue]
		random.shuffle(id_queue)

		self.playbin_lock.lock()

		song = None
		for id_ in id_queue:
			song = monophony.backend.yt.get_similar_song(id_, ignore = id_queue)
			if song:
				break
		else: # nobreak
			song = random.choice(self.queue)

		self.queue.append(song)
		self.index += 1
		self.playback_retries = 0
		self.playbin_lock.unlock()
		self.play_song(song['id'], song['title'])

	def toggle_pause(self):
		state = self.playbin.get_state(Gst.CLOCK_TIME_NONE)[1]

		if state == Gst.State.PLAYING:
			self.playbin.set_state(Gst.State.PAUSED)
		else:
			self.playbin.set_state(Gst.State.PLAYING)

	def next_song(self):
		self.playback_retries = 0
		self._remake_playbin()

		queue_length = len(self.queue)
		song = None
		if self.shuffle and queue_length > 1:
			random_index = self.index
			while random_index == self.index:
				random_index = random.randrange(0, queue_length)

			self.index = random_index
			song = self.queue[self.index]
		elif queue_length - 1 > self.index :
			self.index += 1
			self.playback_retries = 0
			song = self.queue[self.index]

		if song:
			self.play_song(song['id'], song['title'])
			return

		self.play_radio_song()

	def previous_song(self):
		self.playbin.set_state(Gst.State.READY)
		self.index -= 1
		self.playback_retries = 0

		if self.index < 0:
			self.index = 0

		if len(self.queue) > 0:
			song = self.queue[self.index]
			self.play_song(song['id'], song['title'])

	def play_queue(self, queue: list, index: int):
		if len(queue) == 0:
			return

		self.queue = queue
		self.index = index
		self.playback_retries = 0
		song = queue[index]
		self.play_song(song['id'], song['title'])

	def unqueue_song(self):
		if len(self.queue) > 0:
			self.queue.pop(self.index)
			self.index = self.index - 1 if self.index else 0
			self.next_song()

	def queue_song(self, song: dict):
		if not self.queue:
			self.play_song(song['id'], song['title'])

		self.queue.append(song)

	def set_volume(self, volume: float):
		self.playbin.set_property('volume', volume)

	def seek(self, target: float):
		duration = self.playbin.query_duration(Gst.Format.TIME)[1]

		if duration > 0:
			self.playbin.seek_simple(
				Gst.Format.TIME,
				Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
				round(duration * target)
			)
