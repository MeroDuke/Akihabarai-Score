# Desktop Adapter Boundary

Desktop-only operations are isolated in:

```text
app/adapters/qt_desktop_adapter.py
```

This adapter owns:

- Qt clipboard text and pixmap writes
- widget-to-`QPixmap` rendering
- `QPixmap` background trimming
- Qt event processing required before image capture
- native URL opening through `QDesktopServices`
- standard message-box operations
- modal dialog execution

Application and domain services must not import `QApplication`,
`QGuiApplication`, `QPainter`, `QPixmap`, `QDesktopServices`, or `QUrl` to
perform these platform operations. Existing service modules may remain as thin
compatibility facades while callers are migrated.

Content generation stays outside this adapter. It receives already prepared
text or a Qt presentation object and performs only the requested desktop
operation. This boundary is intended to allow a future WebUI adapter to reuse
the same application content and domain state without importing PyQt.
