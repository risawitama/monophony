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

		stack = Gtk.Stack()
		stack.add_titled(MonophonyLibraryPage(), 'library', _('Library'))
		stack.add_titled(MonophonySearchPage(), 'search', _('Search'))

		stack_switcher = Gtk.StackSwitcher()
		stack_switcher.set_stack(stack)

		header_bar = Adw.HeaderBar()
		header_bar.set_title_widget(stack_switcher)

		footer_bar = Adw.HeaderBar()
		footer_bar.set_decoration_layout('')
		footer_bar.set_title_widget(MonophonyPlayer())
		footer_bar.set_valign(Gtk.Align.END)

		box_content = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		box_content.append(header_bar)
		box_content.append(stack)
		box_content.append(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
		box_content.append(footer_bar)
		self.set_content(box_content)
