#!/usr/bin/env python3

import gettext, os

import monophony.backend.cache
from monophony import LANGUAGES
from monophony.frontend.app import MonophonyApplication


def main():
	lang = os.getenv('LANG', 'en_US.UTF-8')
	chosen_lang = 'en'
	for l in LANGUAGES:
		if lang.split('_')[0] == l:
			chosen_lang = l
			break

	if os.getenv('container', '') != 'flatpak':
		gettext.translation('monophony', languages = [chosen_lang]).install()
	else:
		gettext.translation(
			'monophony',
			localedir = '/app/share/locale',
			languages = [chosen_lang]
		).install()

	monophony.backend.cache.clean_up()
	MonophonyApplication().run()


if __name__ == '__main__':
	main()
