import monophony.backend.history

from monophony.frontend.pages.artist_page import MonophonyArtistPage
from monophony.frontend.pages.results_page import MonophonyResultsPage
from monophony.frontend.widgets.recent_searches import MonophonyRecentSearches

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gtk


class MonophonySearchTab(Gtk.Box):
	def __init__(self, player: object):
		super().__init__(orientation=Gtk.Orientation.VERTICAL)

		self.ent_search = Gtk.SearchEntry()
		self.ent_search.set_placeholder_text(_('Enter text or paste a URL...'))
		self.ent_search.set_hexpand(True)
		self.ent_search.set_halign(Gtk.Align.FILL)
		self.ent_search.connect('activate', lambda e: self._on_search(e.get_text()))

		self.btn_back = Gtk.Button.new_from_icon_name('go-previous-symbolic')
		self.btn_back.set_tooltip_text(_('Go back'))
		self.btn_back.set_visible(False)
		self.btn_back.connect('clicked', lambda _b: self._on_back_clicked())

		box_search = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		box_search.set_spacing(5)
		box_search.append(self.btn_back)
		box_search.append(self.ent_search)

		self.box_recents = MonophonyRecentSearches(self._on_search)

		box_search_meta = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		box_search_meta.set_spacing(8)
		box_search_meta.append(box_search)
		box_search_meta.append(self.box_recents)

		clm_search = Adw.Clamp()
		clm_search.set_child(box_search_meta)

		search_bar = Gtk.SearchBar()
		search_bar.add_css_class('inline')
		search_bar.set_show_close_button(False)
		search_bar.set_search_mode(True)
		search_bar.set_child(clm_search)
		search_bar.set_key_capture_widget(self.ent_search)
		self.append(search_bar)

		self.pge_results = MonophonyResultsPage(player)
		self.pge_results.set_vexpand(True)
		self.pge_results.set_valign(Gtk.Align.FILL)
		self.append(self.pge_results)
		self.pge_detail_results = None

		self.set_vexpand(True)
		self.player = player

	def _on_back_clicked(self):
		self.btn_back.set_visible(False)
		self.pge_results.set_visible(True)
		if self.pge_detail_results:
			self.remove(self.pge_detail_results)
			self.pge_detail_results = None

	def show_artist(self, artist: str):
		self.btn_back.set_visible(True)
		self.pge_results.set_visible(False)
		if self.pge_detail_results:
			self.remove(self.pge_detail_results)

		self.pge_detail_results = MonophonyArtistPage(self.player, artist)
		self.pge_detail_results.set_vexpand(True)
		self.pge_detail_results.set_valign(Gtk.Align.FILL)
		self.append(self.pge_detail_results)

	def show_more(self, query: str, filter_: str):
		self.btn_back.set_visible(True)
		self.pge_results.set_visible(False)
		if self.pge_detail_results:
			self.remove(self.pge_detail_results)

		self.pge_detail_results = MonophonyResultsPage(self.player, query, filter_)
		self.pge_detail_results.set_vexpand(True)
		self.pge_detail_results.set_valign(Gtk.Align.FILL)
		self.append(self.pge_detail_results)

	def _on_search(self, text: str):
		self.ent_search.set_text(text)
		if not text:
			return

		if monophony.backend.history.add_search(text):
			self.box_recents.add_search(text)
		self.btn_back.set_visible(False)
		if self.pge_results:
			self.remove(self.pge_results)
		if self.pge_detail_results:
			self.remove(self.pge_detail_results)
			self.pge_detail_results = None

		self.pge_results = MonophonyResultsPage(self.player, text)
		self.pge_results.set_vexpand(True)
		self.pge_results.set_valign(Gtk.Align.FILL)
		self.append(self.pge_results)
