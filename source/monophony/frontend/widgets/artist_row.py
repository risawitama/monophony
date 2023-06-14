import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, GLib, Gtk


class MonophonyArtistRow(Adw.ActionRow):
	def __init__(self, artist: dict, page: Gtk.Widget):
		super().__init__()

		self.artist = artist

		btn_view = Gtk.Button.new_from_icon_name('go-next-symbolic')
		btn_view.set_tooltip_text(_('View Artist'))
		btn_view.set_vexpand(False)
		btn_view.set_valign(Gtk.Align.CENTER)
		btn_view.set_has_frame(False)
		btn_view.connect(
			'clicked', lambda b, p: p.show_artist(self.artist['id']), page
		)
		self.add_suffix(btn_view)
		self.set_tooltip_text(_('View Artist'))
		self.set_property('activatable', True)
		self.connect('activated', lambda b, p: p.show_artist(self.artist['id']), page)

		self.set_title(GLib.markup_escape_text(
			artist['author'] if 'author' in artist and artist['author'] else '________',
			-1
		))
