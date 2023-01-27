prefix = /usr

INSTALL = install -D
INSTALL_DATA = ${INSTALL} -m 644
UNINSTALL = rm -rf


install:
	@# app binary
	mkdir -p $(prefix)/bin/
	python3 -m nuitka bin/monophony.py --remove-output --clean-cache=all --disable-cache=all --follow-import-to=monophony -o $(prefix)/bin/monophony

	@# desktop file
	$(INSTALL_DATA) data/monophony.desktop $(prefix)/share/applications/com.gitlab.zehkira.Monophony.desktop

	@# metainfo
	$(INSTALL_DATA) data/metainfo.xml $(prefix)/share/metainfo/com.gitlab.zehkira.Monophony.metainfo.xml

	@# icons
	$(INSTALL_DATA) data/icons/scalable.svg $(prefix)/share/icons/hicolor/scalable/apps/com.gitlab.zehkira.Monophony.svg
	$(INSTALL_DATA) data/icons/symbolic.svg $(prefix)/share/icons/hicolor/symbolic/apps/com.gitlab.zehkira.Monophony-symbolic.svg
	$(INSTALL_DATA) data/icons/128.png $(prefix)/share/icons/hicolor/128x128/apps/com.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/16.png $(prefix)/share/icons/hicolor/16x16/apps/com.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/192.png $(prefix)/share/icons/hicolor/192x192/apps/com.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/22.png $(prefix)/share/icons/hicolor/22x22/apps/com.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/24.png $(prefix)/share/icons/hicolor/24x24/apps/com.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/256.png $(prefix)/share/icons/hicolor/256x256/apps/com.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/32.png $(prefix)/share/icons/hicolor/32x32/apps/com.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/36.png $(prefix)/share/icons/hicolor/36x36/apps/com.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/384.png $(prefix)/share/icons/hicolor/384x384/apps/com.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/48.png $(prefix)/share/icons/hicolor/48x48/apps/com.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/512.png $(prefix)/share/icons/hicolor/512x512/apps/com.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/64.png $(prefix)/share/icons/hicolor/64x64/apps/com.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/72.png $(prefix)/share/icons/hicolor/72x72/apps/com.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/96.png $(prefix)/share/icons/hicolor/96x96/apps/com.gitlab.zehkira.Monophony.png

	@# translations
	$(INSTALL_DATA) locales/en/LC_MESSAGES/all.mo $(prefix)/share/locale/en/LC_MESSAGES/monophony.mo
	$(INSTALL_DATA) locales/de/LC_MESSAGES/all.mo $(prefix)/share/locale/de/LC_MESSAGES/monophony.mo
	$(INSTALL_DATA) locales/pl/LC_MESSAGES/all.mo $(prefix)/share/locale/pl/LC_MESSAGES/monophony.mo
	$(INSTALL_DATA) locales/sv/LC_MESSAGES/all.mo $(prefix)/share/locale/sv/LC_MESSAGES/monophony.mo
	$(INSTALL_DATA) locales/it/LC_MESSAGES/all.mo $(prefix)/share/locale/it/LC_MESSAGES/monophony.mo
	$(INSTALL_DATA) locales/fr/LC_MESSAGES/all.mo $(prefix)/share/locale/fr/LC_MESSAGES/monophony.mo
	$(INSTALL_DATA) locales/ru/LC_MESSAGES/all.mo $(prefix)/share/locale/ru/LC_MESSAGES/monophony.mo
	$(INSTALL_DATA) locales/nl/LC_MESSAGES/all.mo $(prefix)/share/locale/nl/LC_MESSAGES/monophony.mo

	@# license
	$(INSTALL_DATA) LICENSE $(prefix)/share/licenses/monophony/LICENSE


uninstall:
	@# script file
	$(UNINSTALL) $(prefix)/bin/monophony

	@# desktop file
	$(UNINSTALL) $(prefix)/share/applications/com.gitlab.zehkira.Monophony.desktop

	@# metainfo
	$(UNINSTALL) $(prefix)/share/metainfo/com.gitlab.zehkira.Monophony.metainfo.xml

	@# icons
	$(UNINSTALL) $(prefix)/share/icons/hicolor/*/apps/com.gitlab.zehkira.Monophony*

	@# translations
	$(UNINSTALL) $(prefix)/share/locale/*/LC_MESSAGES/monophony.mo

	@# license
	$(UNINSTALL) $(prefix)/share/licenses/monophony/
