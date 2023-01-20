#!/usr/bin/env python3

import gettext, os

from monophony.frontend.app import MonophonyApplication


def main():
	languages = ['en', 'de', 'pl', 'sv', 'it', 'fr', 'ru', 'nl']
	if os.getenv('container', '') != 'flatpak':
		gettext.translation('monophony', languages = languages).install()
	else:
		gettext.translation(
			'monophony',
			localedir = '/app/share/locale',
			languages = languages
		).install()

	MonophonyApplication().run()


if __name__ == '__main__':
	main()
