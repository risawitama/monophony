## Official packages

The recommended way to install Monophony is using the Flatpak package hosted on GitLab. This package is always the first to receive updates.

| Repository | Package |
| - | - |
| GitLab | [io.gitlab.zehkira.Monophony](https://gitlab.com/zehkira/monophony/-/raw/master/source/data/monophony.flatpakref?ref_type=heads&inline=false) |
| Flathub | [io.gitlab.zehkira.Monophony](https://flathub.org/apps/details/io.gitlab.zehkira.Monophony) |

## Community packages

These packages are maintained by third parties.

| Repository | Package | Version |
| - | - | - |
| Arch User Repository | [monophony](https://aur.archlinux.org/packages/monophony) | ![](https://repology.org/badge/version-for-repo/aur/monophony.svg?header=) |
| Nixpkgs | [monophony](https://search.nixos.org/packages?channel=unstable&show=monophony&type=packages) | ![](https://repology.org/badge/version-for-repo/nix_unstable/monophony.svg?header=) |
| Snap | [monophony](https://snapcraft.io/monophony) | ![](https://img.shields.io/badge/N%2FA-grey) |

## Building from source

Follow these steps to build the app from source for testing purposes:

1. Install `git` and `flatpak-builder`
2. Download the repository: `git clone https://gitlab.com/zehkira/monophony.git`
3. Enter the source directory: `cd monophony/source`
4. Build and install the app as a Flatpak: `make flatpak`
