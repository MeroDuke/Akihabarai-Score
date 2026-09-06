# Repository instructions

## Local Qt test execution

- Run local pytest commands that may create Qt widgets in headless mode by setting
  `QT_QPA_PLATFORM=offscreen` before starting pytest.
- On PowerShell, use:
  `$env:QT_QPA_PLATFORM = "offscreen"; python -m pytest ...`
- Do not show test-created Qt windows on the user's desktop unless the user
  explicitly requests a visible UI test.
