import monophony.backend.history

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango


class MonophonyRecentSearches(Gtk.Box):
	def __init__(self, search_callback: callable):
		super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

		self.children = []
		self.set_visible(False)
		self.set_spacing(4)
		self.set_hexpand(True)
		self.set_halign(Gtk.Align.FILL)
		self.search_callback = search_callback

		searches = monophony.backend.history.read_searches()
		searches.reverse()
		for query in searches:
			self.add_search(query)

	def add_search(self, query: str):
		self.set_visible(True)
		lbl_query = Gtk.Label.new(query)
		lbl_query.set_ellipsize(Pango.EllipsizeMode.END)
		btn_search = Gtk.Button.new()
		btn_search.set_child(lbl_query)
		btn_search.set_hexpand(True)
		btn_search.set_halign(Gtk.Align.FILL)
		btn_search.connect(
			'clicked', lambda b: self._on_search(b.get_child().get_label())
		)
		btn_remove = Gtk.Button.new_from_icon_name('list-remove-symbolic')
		btn_remove.set_tooltip_text(_('Remove'))
		btn_remove.connect(
			'clicked',
			lambda b, q: self._on_remove_search(b, q),
			query
		)
		box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		box.set_hexpand(True)
		box.set_halign(Gtk.Align.FILL)
		box.append(btn_search)
		box.append(btn_remove)
		box.add_css_class('linked')

		if len(self.children) > 2:
			self.remove(self.children[0])
			self.children.pop(0)
		self.children.append(box)
		self.prepend(box)

	def _on_search(self, query: str):
		self.search_callback(query)

	def _on_remove_search(self, btn: Gtk.Button, query: str):
		monophony.backend.history.remove_search(query)
		self.remove(btn.get_parent())
		if not monophony.backend.history.read_searches():
			self.set_visible(False)
