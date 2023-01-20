from monophony import APP_ID
from monophony.frontend.windows.main_window import MonophonyMainWindow

import gi
gi.require_version('Adw', '1')
from gi.repository import Adw, Gio


class MonophonyApplication(Adw.Application):
	def __init__(self):
		super().__init__(
			application_id = APP_ID,
			flags = Gio.ApplicationFlags.FLAGS_NONE
		)

	def do_activate(self):
		self.window = MonophonyMainWindow(
			application = self
		)
		self.window.present()
