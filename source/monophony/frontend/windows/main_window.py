import monophony.backend.player
from monophony import __version__, APP_ID
from monophony.frontend.pages.library_page import MonophonyLibraryPage
from monophony.frontend.pages.search_page import MonophonySearchPage
from monophony.frontend.widgets.player import MonophonyPlayer

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gtk


class MonophonyMainWindow(Adw.ApplicationWindow):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.player = monophony.backend.player.Player()

		stack = Adw.ViewStack()
		stack.add_titled_with_icon(
			MonophonyLibraryPage(self.player),
			'library',
			_('Library'),
			'folder-music-symbolic'
		)
		stack.add_titled_with_icon(
			MonophonySearchPage(self.player),
			'search',
			_('Search'),
			'system-search-symbolic'
		)
		view_switcher = Adw.ViewSwitcher()
		view_switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)
		view_switcher.set_stack(stack)

		btn_about = Gtk.Button.new_with_label(_('About'))
		btn_about.set_has_frame(False)
		box_menu = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		box_menu.append(btn_about)
		pop_menu = Gtk.Popover.new()
		pop_menu.set_child(box_menu)
		btn_about.connect('clicked', self._on_about_clicked, pop_menu)
		btn_menu = Gtk.MenuButton()
		btn_menu.set_icon_name('open-menu-symbolic')
		btn_menu.set_popover(pop_menu)

		header_bar = Adw.HeaderBar()
		header_bar.set_title_widget(view_switcher)
		header_bar.pack_end(btn_menu)

		footer_bar = Adw.HeaderBar()
		footer_bar.set_decoration_layout('')
		footer_bar.set_title_widget(MonophonyPlayer(self.player))
		footer_bar.set_valign(Gtk.Align.END)

		box_content = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		box_content.append(header_bar)
		box_content.append(stack)
		box_content.append(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
		box_content.append(footer_bar)
		self.set_content(box_content)

	def _on_about_clicked(self, _b, parent: Gtk.Popover):
		parent.popdown()

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
		win_about.set_translator_credits(_('translator-credits'))
		win_about.add_credit_section(_('Patrons'), ['yuanca'])
		win_about.set_issue_url('https://gitlab.com/zehkira/monophony/-/issues')
		win_about.add_link(_('Donate'), 'https://www.patreon.com/zehkira')
		win_about.set_website('https://gitlab.com/zehkira/monophony')
		win_about.set_transient_for(self)
		win_about.show()
