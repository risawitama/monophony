#!/usr/bin/env python3

import gettext, os

import monophony.backend.cache
from monophony.frontend.app import MonophonyApplication


def main():
	path = None
	snap_path = os.getenv('SNAP')

	# yes, "container" env really is lowercase for some reason
	if os.getenv('container', '') == 'flatpak': # noqa: SIM112
		path = '/app/share/locale'
	elif snap_path:
		path = os.path.join(snap_path, 'share/locale')

	gettext.translation('monophony', path, fallback=True).install()
	monophony.backend.cache.clean_up()
	MonophonyApplication().run()


if __name__ == '__main__':
	main()
