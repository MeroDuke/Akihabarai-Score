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

The Linux native inventory still needs mapping to distribution source
packages. Libraries supplied by the build host may have independent GPL/LGPL
corresponding-source duties that are not covered by the Qt archives.

## Application source

The public Git repository and version tag identify the exact Akihabarai Score
source used for each release. This remains separate from the upstream runtime
source archives listed above.
