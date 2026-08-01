# Linux runtime contract

The binary release targets Ubuntu 24.04 x86_64 as its validated Linux runtime
baseline. It bundles the pinned CPython, PyQt6, and Qt wheel runtime, but relies
on the operating system for libraries normally installed under `/lib` and
`/usr/lib`.

From a source checkout, install the runtime package set with:

```bash
sudo xargs -a packaging/linux/ubuntu-24.04-runtime-packages.txt apt-get install -y
```

From an extracted portable release, use the copy shipped next to this document:

```bash
sudo xargs -a docs/ubuntu-24.04-runtime-packages.txt apt-get install -y
```

The release CI installs this exact list before running the packaged startup
smoke test. `xvfb` is installed separately as a CI-only headless display tool
and is not an application runtime dependency.

Other Debian-derived distributions may work when they provide ABI-compatible
libraries, but they are not represented as validated by this package list.
Supporting another distribution or baseline requires a separate clean-system
smoke test and its own package mapping.

## Debian compatibility observation

The portable build from application commit
`595247e280c545ed661df84088bcc52a29ac65c1` was manually smoke-tested on
Debian GNU/Linux 13.6 (Trixie) x86_64 in a Hyper-V virtual machine on
2026-08-01.

On the first launch, Qt found its XCB platform plugin but could not load it
because the host did not provide `libxcb-cursor.so.0`. Installing the Debian
package below resolved the startup failure:

```bash
sudo apt update
sudo apt install libxcb-cursor0
```

Afterwards, the application started and its main scoring, localization,
AniList, mode-switching, Tier Board, and export flows passed a manual smoke
test. Some bottom-row button labels were clipped under the tested Linux Qt
style. This is a compatibility observation, not a declaration of Debian as a
fully supported or CI-validated target. Windows remains the primary platform,
and Ubuntu 24.04 x86_64 remains the automated Linux baseline.
