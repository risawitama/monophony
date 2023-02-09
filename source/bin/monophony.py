#!/usr/bin/env python3

import gettext, os

from monophony.frontend.app import MonophonyApplication


def main():
	lang = os.getenv('LANG', 'en_US.UTF-8')
	chosen_lang = 'en'
	for l in ['en']:
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

	MonophonyApplication().run()


if __name__ == '__main__':
	main()
