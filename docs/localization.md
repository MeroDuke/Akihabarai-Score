# Localization Foundation

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

The current stage establishes catalog ownership and key-based presentation. It
does not yet add a runtime language selector; that remains a separate feature
after the refactor stabilization gate.
