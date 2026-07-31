# Release source availability

## Purpose

Akihabarai Score portable binaries bundle open-source runtimes. This document
records the exact upstream source archives corresponding to the copyleft
components confirmed in the release dependency set. The machine-readable
record is `compliance/source-archives.json`.

## Confirmed source archives

| Component | Version | Official source |
| --- | ---: | --- |
| PyQt6 | 6.11.0 | PyPI source distribution recorded with SHA-256 in the source manifest |
| Qt Base | 6.11.1 | Official Qt `qtbase-everywhere-src-6.11.1.tar.xz` archive recorded with SHA-256 |
| Qt Wayland | 6.11.1 | Official Qt `qtwayland-everywhere-src-6.11.1.tar.xz` archive recorded with SHA-256 |

The release package includes this manifest so a recipient can identify and
verify the exact upstream sources. The URLs and hashes were verified against
the official Qt download service and PyPI release metadata.

## What the manifest does not claim

An upstream URL alone is not treated as proof that every GPL/LGPL source-
delivery obligation has been met. Before `1.0.0`, the chosen application and
Qt licensing route must determine whether the corresponding source archives
must also be mirrored alongside every binary release, and for how long.

GPL-3.0-only was selected. On tag builds, Linux release CI downloads every
archive in `source-archives.json`, verifies its SHA-256 before publication, and
attaches the verified files to the same GitHub release as the Linux binary.
Branch builds validate only the manifest and do not download the large source
archives. GitHub also exposes source archives for the tagged Akihabarai Score
repository revision.

After verification, tag CI extracts Qt license texts, copyright/NOTICE files,
REUSE metadata, and `qt_attribution.json` records from the Qt Base and Qt
Wayland sources. These files are placed directly under `licenses/qt-source` in
the Linux portable package before it is archived. The complete original source
archives remain separate release assets.

The same directory contains `qt-attributions.json`, a machine-readable index
of every upstream attribution record found in those pinned source modules. Its
scope field deliberately states that this conservative source-module list is
not an exact claim about which optional third-party code the upstream binary
wheel compiled in.

Linux operating-system libraries are no longer copied into the application
binary. They are supplied by the documented Ubuntu runtime baseline and are
outside the release payload inventory.

## Application source

The public Git repository and version tag identify the exact Akihabarai Score
source used for each release. This remains separate from the upstream runtime
source archives listed above.
