#!/usr/bin/env python3

import gettext, os

import monophony.backend.cache
from monophony.frontend.app import MonophonyApplication


def main():
	if os.getenv('container', '') != 'flatpak':
		gettext.bindtextdomain('monophony')
		gettext.translation('monophony').install()
	else:
		gettext.bindtextdomain('monophony', '/app/share/locale')
		gettext.translation('monophony', '/app/share/locale').install()

	monophony.backend.cache.clean_up()
	MonophonyApplication().run()


if __name__ == '__main__':
	main()
