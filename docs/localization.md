# Runtime Localization

The application uses stable internal identifiers for behavior and translation
keys for user-facing text.

Examples of behavior identifiers:

```text
scored
freehand
manual
online
offline
```

These identifiers must not be translated. Presentation code maps them to keys
such as:

```text
app_mode.scored.label
app_mode.freehand.label
title_mode.online.button
result.strengths
dialog.tier_clear.message
```

Catalogs use UTF-8 JSON:

```json
{
  "language": "hu",
  "messages": {
    "dialog.yes": "Igen"
  }
}
```

Hungarian (`hu`) is the default and fallback language. Missing catalogs,
invalid JSON, and missing keys fall back to the built-in Hungarian messages.
If a key is also absent from the fallback, the stable key itself is returned
so missing translations remain visible and diagnosable.

The desktop UI supports runtime switching between Hungarian and English. The
single language button applies the selected catalog immediately to static and
dynamic widgets, current result content, Tier cards, dialogs, clipboard text,
and image exports. AniList titles and other external or user-authored data are
not translated.

The selected language is stored in a user-scoped JSON file and restored on the
next startup. This preference layer is independent from Qt so a future WebUI
can use an equivalent storage adapter without changing localization behavior.

Default preference locations:

```text
Windows: %APPDATA%\AkihabaraiScore\preferences.json
Linux:   $XDG_CONFIG_HOME/akihabarai-score/preferences.json
         or ~/.config/akihabarai-score/preferences.json
```

The current schema is deliberately extensible:

```json
{
  "schema_version": 1,
  "ui": {
    "language": "en"
  }
}
```

Language-change logs share a request identifier across the Qt request,
localization service, catalog lookup/load, preference save, and UI application
events. Missing translation keys are logged once per language and key to avoid
repeated warnings.

Both `config/locales/hu.json` and `config/locales/en.json` are required in the
portable desktop package. Windows and Linux CI validate their presence, launch
the packaged application layout, and reserve package publication for tagged
GitHub releases.

## Manual Babel layout stress test

`tools/localization/babel.json` is a development-only catalog. For every key it
contains the longer existing value selected from the Hungarian and English
production catalogs; it never introduces invented or expanded text. It is not
a supported language, is not exposed by the application, is not used by
CI/CD, and is outside every release package. Use it manually when adding a
language or changing the Qt UI.

The application must be switched to Hungarian and closed before the test,
because the last selected language is stored in user preferences. From a clean
working tree, temporarily replace the default catalog:

```powershell
Rename-Item config/locales/hu.json hu.production.json
Copy-Item tools/localization/babel.json config/locales/hu.json
python -m app.main
```

Exercise the relevant UI states at the supported minimum window size. After
closing the application, restore the production catalog immediately:

```powershell
Remove-Item config/locales/hu.json
Rename-Item config/locales/hu.production.json hu.json
git status --short
```

The final status check must not report a change to `config/locales/hu.json` or
an untracked backup catalog. Never build, commit, or publish while the Babel
catalog occupies the production path.
