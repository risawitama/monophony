import contextlib, random, time

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
	LOOP_SONG = 1
	LOOP_QUEUE = 2
	RADIO = 3


class Player:
	def __init__(self):
		Gst.init([])
		self.lock = GLib.Mutex()
		self.interrupt = False
		self.paused = False
		self.buffering = False
		self.index = 0
		self.queue = []
		self.recent_songs = []
		self.next_fetch_lock = GLib.Mutex()
		self.next_stream_url = ''
		self.next_expected_id = ''
		self.next_fetch_time = 0
		self.last_progress = 0
		self.mode = int(
			monophony.backend.settings.get_value('mode', PlaybackMode.NORMAL)
		)
		self.mpris_adapter = None
		self.mpris_server = None
		self.ui_update_callback = None
		self.queue_change_callback = None
		self.queue_end_callback = None
		self.raise_callback = None
		self.playbin = Gst.ElementFactory.make('playbin3', 'playbin3')
		self.playbin.set_state(Gst.State.READY)
		self.playbin.get_bus().add_signal_watch()
		self.playbin.get_bus().connect('message::error', self._on_bus_error)
		self.playbin.get_bus().connect('message::stream-start', self._on_song_start)
		self.playbin.get_bus().connect('message::buffering', self._on_buffering)
		self.playbin.get_bus().connect(
			'message::eos', lambda *_: GLib.Thread.new(None, self._on_song_end)
		)

	### --- UTILITY METHODS --- ###

	def terminate(self):
		self.lock.lock()
		self.playbin.set_state(Gst.State.NULL)
		self.mpris_server.unpublish()

	def is_busy(self) -> bool:
		if not self.lock.trylock():
			return True

		self.lock.unlock()
		return self.buffering

	def is_paused(self) -> bool:
		return self.paused

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
			with contextlib.suppress(IndexError):
				result = self.queue[self.index]

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

	def _on_buffering(self, _bus, msg):
		self.lock.lock()
		percent = msg.parse_buffering()
		if not self.buffering and percent < 100:
			print('Buffering...')
			self.buffering = True
			self.playbin.set_state(Gst.State.PAUSED)
			GLib.idle_add(
				self.ui_update_callback,
				self.get_current_song(),
				True,
				self.paused,
				False
			)
		elif percent >= 100:
			print('Done buffering')
			self.buffering = False
			if not self.paused:
				self.playbin.set_state(Gst.State.PLAYING)
			GLib.idle_add(
				self.ui_update_callback,
				self.get_current_song(),
				False,
				self.paused,
				False
			)

		self.lock.unlock()

	def _on_bus_error(self, _bus, err):
		print('Playback error:', err.parse_error().gerror.message)
		self.last_progress = self.playbin.query_position(Gst.Format.TIME)[1]
		print('Failed at', self.last_progress)
		GLib.Thread.new(
			None,
			self.play_song,
			self.queue[self.index],
			True,
			True
		)

	def _on_song_start(self, _bus, _msg):
		self.lock.lock()
		if not self.buffering:
			print('No buffering occured at start of stream')
			self.playbin.set_state(Gst.State.PLAYING)
			GLib.idle_add(
				self.ui_update_callback, self.get_current_song(), False, False, True
			)

		if self.last_progress > 0:
			print('Seeking to', self.last_progress)
			self.playbin.seek_simple(
				Gst.Format.TIME,
				Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE,
				self.last_progress
			)

		self.last_progress = 0
		self.lock.unlock()

	def _on_song_end(self):
		self.lock.lock()
		if self.playbin.get_bus().have_pending():
			self.lock.unlock()
			return

		print('Song has ended')
		self.next_song(lock=False)
		self.lock.unlock()

	### --- MISC --- ###

	def fetch_next_song_url(self):
		self.lock.lock()
		i = None
		if self.mode == PlaybackMode.LOOP_SONG:
			i = self.index
		elif self.index < len(self.queue) - 1:
			i = self.index + 1
		elif self.mode == PlaybackMode.LOOP_QUEUE:
			i = 0
		if i is None:
			self.lock.unlock()
			return
		song_id = self.queue[i]['id']
		print(f'Fetching stream URL for predicted song {song_id}...')
		self.lock.unlock()

		self.next_fetch_lock.lock()
		url = monophony.backend.yt.get_song_uri(song_id)
		if url:
			self.next_expected_id = song_id
			self.next_stream_url = url
			self.next_fetch_time = time.time()

		print('Done fetching')
		self.next_fetch_lock.unlock()

	### --- PLAYBACK CONTROLS --- ###

	def play_song(self, song: dict, lock: bool=False, resume: bool=False):
		if lock:
			self.lock.lock()

		GLib.idle_add(self.ui_update_callback, song, True, False, True)
		GLib.idle_add(self.queue_change_callback)
		if not resume:
			print('Playing', song['id'])
			self.last_progress = 0
		else:
			print('Resuming', song['id'])

		if song['id'] not in self.recent_songs:
			self.recent_songs.append(song['id'])
		monophony.backend.history.add_song(song)
		self.playbin.set_state(Gst.State.READY)

		print('Attempting to get song from cache...')
		uri = monophony.backend.cache.get_song_uri(song['id'])

		if not uri:
			print('Attempting to use prepared stream URL...')
			if self.next_fetch_lock.trylock():
				if self.next_stream_url:
					if time.time() - self.next_fetch_time < 60 * 5:
						if song['id'] == self.next_expected_id:
							uri = self.next_stream_url
							print('Using prepared stream URL for predicted song')
						else:
							print('Predicted song ID is incorrect!')
					else:
						print('Predicted song stream URL is too old!')
				else:
					print('No stream URL prepeared!')

				self.next_fetch_lock.unlock()
			else:
				print('Predicted song stream URL is not yet ready!')

		if not uri:
			print('Fetching stream from YT...')
			while True:
				uri = monophony.backend.yt.get_song_uri(song['id'])
				if uri is not None:
					break
				if self.interrupt:
					if lock:
						self.lock.unlock()
					return

		print('Starting playback')
		self.playbin.set_property('uri', uri)
		self.paused = False
		# buffering expected, so don't actually start yet (unless offline)
		self.playbin.set_state(Gst.State.PAUSED)
		self.mpris_server.unpublish()
		self.mpris_server.publish()
		self.mpris_adapter.emit_all()
		self.mpris_adapter.on_playback()
		GLib.idle_add(self.ui_update_callback, song, True, False, True)

		GLib.Thread.new(None, self.fetch_next_song_url)

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
		if self.buffering:
			self.lock.unlock()
			return

		if not self.paused:
			self.playbin.set_state(Gst.State.PAUSED)
			self.paused = True
		else:
			self.playbin.set_state(Gst.State.PLAYING)
			self.paused = False

		self.mpris_adapter.on_playpause()
		GLib.idle_add(
			self.ui_update_callback,
			self.get_current_song(),
			False,
			self.paused,
			False
		)
		self.lock.unlock()

	def next_song(self, ignore_loop: bool=False, lock: bool=True):
		if lock and not self.lock.trylock():
			return

		queue_length = len(self.queue)
		song = None
		if self.mode == PlaybackMode.LOOP_SONG and not ignore_loop:
			song = self.queue[self.index]
		elif queue_length - 1 > self.index:
			self.index += 1
			song = self.queue[self.index]
		elif self.mode == PlaybackMode.LOOP_QUEUE:
			self.index = 0
			song = self.queue[self.index]

		if song:
			self.play_song(song)
		elif self.mode == PlaybackMode.RADIO:
			self.play_radio_song()
		else:
			self.clear_queue(lock=False)

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

	def clear_queue(self, lock: bool=True):
		if lock:
			self.lock.lock()

		self.playbin.set_state(Gst.State.NULL)
		self.playbin.set_property('uri', '')
		self.queue = []
		self.index = 0
		self.mpris_server.unpublish()
		GLib.idle_add(self.queue_change_callback)
		GLib.idle_add(self.ui_update_callback, None, False, False, False)
		GLib.idle_add(self.queue_end_callback)

		if lock:
			self.lock.unlock()

	def shuffle_queue(self):
		self.lock.lock()
		song = self.get_current_song(lock=False)
		random.shuffle(self.queue)
		if song:
			self.queue.remove(song)
			self.queue.insert(0, song)
			self.index = 0

		GLib.Thread.new(None, self.fetch_next_song_url)
		GLib.idle_add(self.queue_change_callback)

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

		GLib.Thread.new(None, self.fetch_next_song_url)
		GLib.idle_add(self.queue_change_callback)

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

		GLib.Thread.new(None, self.fetch_next_song_url)
		GLib.idle_add(self.queue_change_callback)

		self.lock.unlock()

	def queue_song(self, song: dict):
		self.lock.lock()

		if not self.queue:
			self.play_song(song)

		self.queue.append(song)

		GLib.Thread.new(None, self.fetch_next_song_url)
		GLib.idle_add(self.queue_change_callback)

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
