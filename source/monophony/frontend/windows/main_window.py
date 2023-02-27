import monophony.backend.cache
import monophony.backend.mpris
import monophony.backend.player
import monophony.backend.playlists
import monophony.backend.settings
from monophony import __version__, APP_ID
from monophony.frontend.pages.library_page import MonophonyLibraryPage
from monophony.frontend.pages.search_page import MonophonySearchPage
from monophony.frontend.widgets.player import MonophonyPlayer
from monophony.frontend.windows.delete_window import MonophonyDeleteWindow
from monophony.frontend.windows.rename_window import MonophonyRenameWindow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gdk, Gio, GLib, Gtk


class MonophonyMainWindow(Adw.ApplicationWindow):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.set_default_size(
			int(monophony.backend.settings.get_value('window-width', 600)),
			int(monophony.backend.settings.get_value('window-height', 500))
		)
		self.player = monophony.backend.player.Player()
		GLib.Thread.new(None, monophony.backend.mpris.init, self.player)

		pge_library = MonophonyLibraryPage(self.player)
		self.pge_search = MonophonySearchPage(self.player)
		self.stack = Adw.ViewStack()
		self.stack.add_named(pge_library, 'library')
		self.stack.add_named(self.pge_search, 'search')

		self.btn_back = Gtk.Button.new_from_icon_name('go-previous-symbolic')
		self.btn_back.hide()
		self.btn_back.connect('clicked', self._on_back_clicked)

		btn_about = Gtk.Button.new_from_icon_name('help-about-symbolic')
		btn_about.set_tooltip_text(_('About'))
		btn_about.set_has_frame(False)
		btn_about.connect('clicked', self._on_about_clicked)

		self.ent_search = Gtk.SearchEntry()
		self.ent_search.set_property('placeholder-text', _('Search for content...'))
		self.ent_search.set_hexpand(True)
		self.ent_search.set_halign(Gtk.Align.FILL)
		self.ent_search.connect('activate', self._on_search)
		clm_search = Adw.Clamp.new()
		clm_search.set_child(self.ent_search)

		header_bar = Adw.HeaderBar()
		header_bar.pack_start(self.btn_back)
		header_bar.set_title_widget(clm_search)
		header_bar.pack_end(btn_about)

		box_content = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		box_content.append(header_bar)
		box_content.append(self.stack)
		box_content.append(MonophonyPlayer(self.player))
		self.set_content(box_content)

		self.install_action(
			'quit-app', None, (lambda w, a, t: w.close())
		)
		self.install_action(
			'focus-search', None, (lambda w, a, t: w.ent_search.grab_focus())
		)
		self.get_application().set_accels_for_action('quit-app', ['<Control>w', '<Control>q'])
		self.get_application().set_accels_for_action('focus-search', ['<Control>f'])
		self.connect('close-request', MonophonyMainWindow._on_quit)

	def _on_quit(self):
		size = self.get_default_size()
		monophony.backend.settings.set_value('window-width', size.width)
		monophony.backend.settings.set_value('window-height', size.height)

	def _on_search(self, ent: Gtk.Entry):
		self.btn_back.show()
		self.stack.set_visible_child_name('search')
		self.pge_search._on_search(ent)

	def _on_back_clicked(self, _b):
		self.btn_back.hide()
		self.stack.set_visible_child_name('library')
		self.pge_search.clear()
		self.ent_search.set_text('')

	def _on_about_clicked(self, _b):
		win_about = Adw.AboutWindow.new()
		win_about.set_application_icon(APP_ID)
		win_about.set_application_name('Monophony')
		win_about.set_version(__version__)
		win_about.set_copyright('Copyright © 2022-2023 zehkira')
		win_about.set_license_type(Gtk.License.CUSTOM)
		win_about.set_license(
	'''Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'''
		)
		win_about.add_legal_section(
			'ytmusicapi',
			'Copyright (c) 2020 sigma67',
			Gtk.License.CUSTOM,
			'''Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''
		)
		win_about.add_legal_section(
			'SponsorBlock',
			'',
			Gtk.License.CUSTOM,
			'Uses SponsorBlock data licensed used under CC BY-NC-SA 4.0 from https://sponsor.ajay.app/.'
		)
		win_about.add_legal_section(
			'mpris_server', '', Gtk.License.AGPL_3_0, None
		)
		win_about.add_legal_section(
			'requests', '', Gtk.License.APACHE_2_0, None
		)
		win_about.set_translator_credits(_('translator-credits'))
		win_about.set_issue_url('https://gitlab.com/zehkira/monophony/-/issues')
		win_about.add_link(_('Donate'), 'https://ko-fi.com/zehkira')
		win_about.set_website('https://gitlab.com/zehkira/monophony')
		win_about.set_transient_for(self)
		win_about.show()

	def _on_queue_song(self, song: dict):
		if song:
			GLib.Thread.new(None, self.player.queue_song, song)

	def _on_move_song(self, song: dict, group: dict, direction: int):
		index = group['contents'].index(song)
		monophony.backend.playlists.swap_songs(
			group['title'], index, index + direction
		)

	def _on_uncache_song(self, song: dict):
		monophony.backend.cache.uncache_song(song['id'])

	def _on_cache_song(self, song: dict):
		GLib.Thread.new(
			None, monophony.backend.cache.cache_song, song['id']
		)

	def _on_new_playlist(self, song: dict):
		def _create(name: str):
			if song:
				monophony.backend.playlists.add_playlist(name, [song])
			else:
				monophony.backend.playlists.add_playlist(name)

		MonophonyRenameWindow(self, _create).show()

	def _on_delete_playlist(self, widget: object):
		MonophonyDeleteWindow(self, widget.group['title']).show()

	def _on_rename_playlist(self, widget: object):
		def _rename(new_name: str):
			success = monophony.backend.playlists.rename_playlist(
				widget.group['title'], new_name
			)
			if success:
				widget.group['title'] = new_name
				widget.set_title(new_name)
			else:
				MonophonyMessageWindow(
					self,
					_('Could not rename'),
					_('Playlist already exists')
				).show()

		MonophonyRenameWindow(self, _rename, widget.group['title']).show()

	def _on_save_playlist(self, name: str, contents: list):
		monophony.backend.playlists.add_playlist(name, contents)
