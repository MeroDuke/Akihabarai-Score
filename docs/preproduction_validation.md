# Pre-production validation notes

This document records reproducible findings from the stabilization period
leading to 1.0.0. It is evidence and a review queue, not a commitment that
every observation will result in a product change.

## Change policy

- Application feature development is frozen until 1.0.0.
- Critical defects and confirmed regressions remain eligible for correction.
- Usability changes require corroborating feedback and explicit acceptance.
- Documentation and release-validation records may continue to improve during
  the freeze.

## Debian 13.6 portable-build smoke test

Date: 2026-08-01

Application commit: `595247e280c545ed661df84088bcc52a29ac65c1`

Environment:

- Debian GNU/Linux 13.6 (Trixie), x86_64;
- Hyper-V virtual machine;
- portable Linux archive produced by the Ubuntu 24.04 GitHub Actions build.

Observed startup failure:

- Qt found `libqxcb.so` but could not load it;
- the host library `libxcb-cursor.so.0` was missing;
- the application window did not appear and the application log remained
  empty because failure occurred during early Qt platform initialization.

Resolution:

```bash
sudo apt update
sudo apt install libxcb-cursor0
```

Result after installing the dependency:

- the application started successfully;
- Hungarian and English localization worked;
- Online/AniList and Offline title entry worked;
- Data-driven and Freehand mode switching worked;
- scoring and Tier Board interactions worked;
- clipboard and image export flows worked;
- no crash or functional regression was observed during the manual smoke test.

This proves practical compatibility with the tested Debian environment after
installing the missing dependency. It does not make Debian a CI-validated or
fully supported target.

## Open Linux packaging and UI observations

These are non-blocking 1.0.0 review candidates:

1. The Linux TAR contains an explicit `./` root entry because it is created
   from `tar ... -C release .`. Some Windows archive viewers display this as a
   separate `[.]` directory. Extraction is correct, but the archive listing is
   less clean than the Windows ZIP listing.
2. The tested Linux Qt style uses different font metrics and control geometry
   from Windows. Some Hungarian labels in the bottom button rows are clipped.
   The main scoring layout, two-line dimension labels, result table, and Tier
   Board remain usable.

Both observations are currently classified as nice-to-have quality
improvements because Windows is the primary target platform and the tested
Linux flows remained functional.

## README transition to the 1.0.0 baseline

Before publishing 1.0.0, review the complete user-facing README as a baseline
product description rather than as a history of the `0.x` releases. A reader
who first encounters the application at 1.0.0 should not need knowledge of
which capabilities were introduced during pre-release development.

Known wording that requires review:

- replace the statement that the project is "close to 1.0" with stable-release
  wording appropriate for the published version;
- remove the historical "new" qualifier from Freehand mode;
- rewrite "the current version received several usability improvements" as a
  direct description of the available interface and usability capabilities;
- check the rest of the README for release-relative wording that assumes the
  reader used an earlier `0.x` build.

Do not remove words merely because they mean "new" in another context. Phrases
about creating a new card, switching language without restarting, or detecting
a newly available release describe current behavior and remain valid at 1.0.0.

The 1.0.0 README should answer what the application is and does at its baseline,
while version-to-version additions belong in the changelog and release notes.
