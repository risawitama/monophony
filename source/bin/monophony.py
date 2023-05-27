#!/usr/bin/env python3

import gettext, os

import monophony.backend.cache
from monophony.frontend.app import MonophonyApplication


def main():
	path = None
	if os.getenv('container', '') == 'flatpak':
		path = '/app/share/locale'

	gettext.translation('monophony', path, fallback = True).install()
	monophony.backend.cache.clean_up()
	MonophonyApplication().run()


if __name__ == '__main__':
	main()
