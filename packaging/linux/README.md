# Linux runtime contract

The binary release targets Ubuntu 24.04 x86_64 as its validated Linux runtime
baseline. It bundles the pinned CPython, PyQt6, and Qt wheel runtime, but relies
on the operating system for libraries normally installed under `/lib` and
`/usr/lib`.

Install the runtime package set with:

```bash
sudo xargs -a packaging/linux/ubuntu-24.04-runtime-packages.txt apt-get install -y
```

The release CI installs this exact list before running the packaged startup
smoke test. `xvfb` is installed separately as a CI-only headless display tool
and is not an application runtime dependency.

Other Debian-derived distributions may work when they provide ABI-compatible
libraries, but they are not represented as validated by this package list.
Supporting another distribution or baseline requires a separate clean-system
smoke test and its own package mapping.
