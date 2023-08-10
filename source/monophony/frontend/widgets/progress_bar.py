import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GLib, Gtk


class MonophonyProgressBar(Gtk.ProgressBar):
	def __init__(self, text: str=''):
		super().__init__()

		self.lock = GLib.Mutex()
		self.target = 100
		self._progress = 0

		if text:
			self.set_text(text)
			self.set_show_text(True)

	def progress(self, step: int=1):
		self._progress += step
		self.set_fraction(self._progress / self.target)
