import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gdk, GObject, Gtk


class MonophonyBigSpinner(Gtk.Spinner):
	def __init__(self):
		super().__init__()

		self.set_halign(Gtk.Align.CENTER)
		self.set_valign(Gtk.Align.CENTER)
		self.set_hexpand(True)
		self.set_vexpand(True)

		self.add_css_class('big-spinner')
		css = Gtk.CssProvider.new()
		css.load_from_data('''
			.big-spinner {
				min-height: 72px;
				min-width: 72px;
			}
		''', -1)
		Gtk.StyleContext.add_provider_for_display(
			Gdk.Display.get_default(),
			css,
			Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)

		self.bind_property(
			'visible',
			self,
			'spinning',
			GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL
		)
