prefix = /usr

INSTALL = install -D
INSTALL_DATA = ${INSTALL} -m 644
UNINSTALL = rm -rf


build:
	python3 -m nuitka bin/monophony.py \
	--show-progress \
	--remove-output \
	--clean-cache=all \
	--follow-import-to=monophony \
	--follow-import-to=ytmusicapi \
	--follow-import-to=mpris_server \
	--follow-import-to=gi \
	-o monophony.bin


install:
	@# app binary
	$(INSTALL) monophony.bin $(prefix)/bin/monophony

	@# desktop file
	$(INSTALL_DATA) data/monophony.desktop $(prefix)/share/applications/io.gitlab.zehkira.Monophony.desktop

	@# metainfo
	$(INSTALL_DATA) data/metainfo.xml $(prefix)/share/metainfo/io.gitlab.zehkira.Monophony.metainfo.xml

	@# icons
	$(INSTALL_DATA) data/icons/scalable.svg $(prefix)/share/icons/hicolor/scalable/apps/io.gitlab.zehkira.Monophony.svg
	$(INSTALL_DATA) data/icons/symbolic.svg $(prefix)/share/icons/hicolor/symbolic/apps/io.gitlab.zehkira.Monophony-symbolic.svg
	$(INSTALL_DATA) data/icons/128.png $(prefix)/share/icons/hicolor/128x128/apps/io.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/16.png $(prefix)/share/icons/hicolor/16x16/apps/io.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/192.png $(prefix)/share/icons/hicolor/192x192/apps/io.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/22.png $(prefix)/share/icons/hicolor/22x22/apps/io.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/24.png $(prefix)/share/icons/hicolor/24x24/apps/io.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/256.png $(prefix)/share/icons/hicolor/256x256/apps/io.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/32.png $(prefix)/share/icons/hicolor/32x32/apps/io.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/36.png $(prefix)/share/icons/hicolor/36x36/apps/io.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/384.png $(prefix)/share/icons/hicolor/384x384/apps/io.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/48.png $(prefix)/share/icons/hicolor/48x48/apps/io.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/512.png $(prefix)/share/icons/hicolor/512x512/apps/io.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/64.png $(prefix)/share/icons/hicolor/64x64/apps/io.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/72.png $(prefix)/share/icons/hicolor/72x72/apps/io.gitlab.zehkira.Monophony.png
	$(INSTALL_DATA) data/icons/96.png $(prefix)/share/icons/hicolor/96x96/apps/io.gitlab.zehkira.Monophony.png

	@# translations
	cd locales; for d in */; do $(INSTALL_DATA) $${d}LC_MESSAGES/all.mo $(prefix)/share/locale/$${d}LC_MESSAGES/monophony.mo; done

	@# license
	$(INSTALL_DATA) LICENSE $(prefix)/share/licenses/monophony/LICENSE


# for testing purposes. builds and installs a flatpak. packages should use
# "make build" and "make install" instead
flatpak:
	flatpak-builder --user --install --force-clean --repo=repo/ build/ data/manifest.json


# updates the trasnslation template
translation:
	find monophony -iname "*.py" | xargs xgettext --omit-header -j -o locales/all.pot


uninstall:
	@# script file
	$(UNINSTALL) $(prefix)/bin/monophony

	@# desktop file
	$(UNINSTALL) $(prefix)/share/applications/io.gitlab.zehkira.Monophony.desktop

	@# metainfo
	$(UNINSTALL) $(prefix)/share/metainfo/io.gitlab.zehkira.Monophony.metainfo.xml

	@# icons
	$(UNINSTALL) $(prefix)/share/icons/hicolor/*/apps/io.gitlab.zehkira.Monophony*

	@# translations
	$(UNINSTALL) $(prefix)/share/locale/*/LC_MESSAGES/monophony.mo

	@# license
	$(UNINSTALL) $(prefix)/share/licenses/monophony/
