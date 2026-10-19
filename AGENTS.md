# Repository instructions

## Release development and integration

- Follow the coordinated-release branch policy: create `release/<version>`
  from the latest stable `main` after the owner accepts the target version and
  scope. Create release feature branches as `feature/<version>/<short-name>`
  from that release branch and merge tested work back into it.
- Use `fix/<version>/<short-name>` branches from the release branch for
  standalone defects found during release development or acceptance testing.
  Direct release-branch changes are limited to integration fixes and release
  metadata/documentation. Do not merge individual release features into `main`.
- An accepted release scope is not permission to add unrelated work. Add,
  remove, or postpone scope items only with owner approval, updating the plan
  and roadmap together.
- The release branch name identifies its target version from the start.
  Set the final application/package version and prepare the changelog during
  release preparation; do not bump versions for individual feature merges.
  Identify intermediate test builds by their embedded commit/build metadata.
  Keep the changelog `Unreleased` until the owner selects the publication date.
- After all accepted work is complete, validate the combined release branch
  with the full relevant regression suite and platform CI before requesting
  approval to merge it into `main`. A merge and a publication/tag are separate
  actions requiring their respective explicit owner approval.
- Create the next release branch from the updated stable `main`, rather than
  continuing development on the previous release branch.
- Start urgent hotfixes from the affected stable `main` using
  `hotfix/<patch-version>/<short-name>`. After the tested hotfix is integrated,
  propagate the applicable fix to every affected active release branch and
  run its relevant regression checks. Preserve each release branch's own
  version/changelog; do not copy obsolete hotfix metadata over them. Record
  propagation, or the reason a branch is unaffected, in the relevant plan.

## Documentation-only work

- The owner may explicitly authorize documentation-only changes directly on
  `main`, including planning and repository instructions. When that permission
  applies to the current documentation session, keep using `main`; do not ask
  again or create a branch for each document. Without such authorization,
  use a separate branch.
- This exception covers prose and planning records only. Application code,
  runtime configuration, dependencies, build scripts, and CI workflow changes
  still follow the development branch policy even when motivated by a
  documentation task.
- Validate documentation with an appropriate diff review and local Markdown
  link checks. Run application tests only when the change affects a tested
  contract or leaves a concrete behavior question to verify. Documentation
  permission does not authorize a merge, tag, release, or deployment.

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
- The required workflow/regression test must be implemented before the feature
  is pushed for CI validation.
- Run the new workflow/regression test locally in headless mode and confirm it
  passes before pushing the feature branch. Do not use CI as the first place to
  discover an automated test failure that can be reproduced locally.
- CI is a second, independent confirmation. A feature is not complete until its
  required workflow/regression test passes both locally and in CI.

## Roadmap and project plans

- At the start of repository work, read `ROADMAP.md` and `plans/README.md`, then
  read every active plan relevant to the requested change. Use them to identify
  the accepted release scope, target version, constraints, and prior decisions.
- `ROADMAP.md` is the release-level overview. It must link to detailed plan
  records instead of duplicating their full content.
- `plans/` contains proposed, accepted, in-progress, deferred, and completed
  development initiatives. Start new non-trivial plans from
  `plans/plan-template.md`.
- Every plan must have a stable plan ID, status, target release or `TBD`, type,
  priority, dates, measurable acceptance criteria, and a test strategy.
- A `TBD` target release is not an implementation commitment. Do not move a
  plan to `in-progress` or expand a release scope until the project owner has
  approved its target version and scope.
- When a plan's scope, target release, status, acceptance criteria, or outcome
  changes, update both the plan and the corresponding `ROADMAP.md` entry in the
  same change.
- Completed plans belong in `plans/completed/` and must record implementation
  evidence such as commits, local tests, CI runs, manual verification, and
  meaningful deviations from the accepted plan.
- Deferred plans belong in `plans/deferred/` and must retain the reason and
  conditions for reconsideration.
- Before closing a minor release, verify that the next planned minor release
  has at least one owner-approved plan or backlog item with an assigned target
  version. The only exception is a reviewed, genuinely empty backlog, which
  must be recorded in `ROADMAP.md`. This gate does not block urgent hotfixes.

## Documentation organization

- `docs/` describes the product and architecture as they currently exist.
  Follow the categories and index in `docs/README.md`.
- Future changes and implementation intentions belong in `plans/`, not in
  current-state technical documentation.
- Decision and validation records may remain under their dedicated `docs/`
  categories when they document evidence or an adopted current-state decision
  rather than future implementation work.
- When moving or renaming documentation, update all source, workflow, test,
  packaging, notice, roadmap, and Markdown references in the same change, then
  verify that local Markdown links resolve.
