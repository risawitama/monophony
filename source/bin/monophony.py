#!/usr/bin/env python3

import gettext, os

import monophony.backend.cache
from monophony.frontend.app import MonophonyApplication


def main():
	path = None
	if os.getenv('container', '') == 'flatpak':
		path = '/app/share/locale'

	try:
		gettext.translation('monophony', path).install()
	except FileNotFoundError:
		gettext.translation('monophony', path, languages = ['en']).install()

	monophony.backend.cache.clean_up()
	MonophonyApplication().run()


if __name__ == '__main__':
	main()
