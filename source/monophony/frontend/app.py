from monophony import APP_ID
from monophony.frontend.windows.main_window import MonophonyMainWindow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gio, Gtk


class MonophonyApplication(Adw.Application):
	def __init__(self):
		super().__init__(
			application_id=APP_ID,
	 		flags=Gio.ApplicationFlags.DEFAULT_FLAGS
		)

	def do_activate(self):
		windows = self.get_windows()

		if len(windows) > 0:
			windows[0].set_visible(True)
		else:
			self.window = MonophonyMainWindow(application=self)
			self.inhibit(self.window, Gtk.ApplicationInhibitFlags.SUSPEND, None)
			self.window.present()
