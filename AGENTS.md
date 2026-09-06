# Repository instructions

## Local Qt test execution

- Run local pytest commands that may create Qt widgets in headless mode by setting
  `QT_QPA_PLATFORM=offscreen` before starting pytest.
- On PowerShell, use:
  `$env:QT_QPA_PLATFORM = "offscreen"; python -m pytest ...`
- Do not show test-created Qt windows on the user's desktop unless the user
  explicitly requests a visible UI test.

## Feature test coverage

- Every new feature must include appropriate unit or low-level tests and at
  least one automated end-user workflow/regression test that exercises a
  complete user-visible path through the implemented behavior.
- Workflow tests must drive the application through user-facing interactions
  where practical, rather than only setting internal state or calling the
  implementation directly.
- External services must not make workflow tests unreliable. Mock or fake
  network APIs in CI unless an explicitly approved integration test requires a
  real service.
- A feature is not complete until its required workflow/regression test passes
  locally and in CI.
