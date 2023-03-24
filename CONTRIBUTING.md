## Bug reports

Include the following information in bug reports:
- Operating system and version (Ubuntu 22.04)
- Desktop environment or window manager (GNOME)
- Installation method (Flatpak from Flathub)

## Translation instructions

Standard translation files are located in `source/locales`. `source/data/metainfo.xml` can also be translated by adding new `<p>` and `<summary>` elements:

```xml
  <summary>Stream music from YouTube</summary>
  <summary xml:lang="de">Musik von YouTube streamen</summary>
  <description>
    <p>
      Listen to your favorite music without using a browser.
    </p>
    <p xml:lang="de">
      Hören Sie Ihre Lieblingsmusik, ohne einen Browser zu verwenden.
    </p>
  </description>
```
