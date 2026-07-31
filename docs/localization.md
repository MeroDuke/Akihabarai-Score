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
the packaged application layout, and publish downloadable portable artifacts.
