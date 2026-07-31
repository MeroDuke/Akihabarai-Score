# Application license decision record

## Scope

This record reviews the goals of Akihabarai Score License 1.0 against the
finished application's actual dependency graph. It does not replace `LICENSE`.
That replacement requires an explicit owner decision.

## Retired custom-license rules

| Existing rule or goal | Technical/legal result | Proposed treatment |
| --- | --- | --- |
| Personal, non-commercial use only | Conflicts with the intended open-use direction and the GPL PyQt6 dependency | Remove |
| Redistribution only in original, unmodified form | Conflicts with open-source modification rights and GPL | Remove |
| Modification and derivative works prohibited | Conflicts with GPL and the stated project direction | Remove |
| Reverse engineering prohibited | Conflicts with GPL and with Qt LGPL debugging/relinking rights | Remove |
| Commercial use requires permission | Conflicts with GPL freedom and the stated project direction | Remove |
| License text and copyright attribution accompany redistribution | Normal and enforceable software-license requirement | Preserve through the selected standard license and release packaging |
| Modified builds may not imply official endorsement | Legitimate brand-protection goal, but not an application copyright restriction | Move to a separate trademark/branding policy |
| A show or video using the application should mention Akihabarai Score | Desirable community norm, but forcing unrelated output attribution is not a clean open-source software-license condition | Publish as a creator guideline; optionally add a visible export credit only through a separate product decision |

The replacement must also contain the standard warranty and liability
disclaimer that the custom license currently lacks.

## Viable dependency and license routes

### Route A: keep community PyQt6 and use GPL-3.0-only

Advantages:

- no UI binding migration;
- no commercial PyQt purchase;
- directly compatible with the confirmed PyQt6 license;
- permits use, modification, redistribution, and commercial activity;
- preserves copyright and license attribution in redistributed copies.

Trade-offs:

- modified and redistributed derivatives must remain GPL-compatible and make
  corresponding source available;
- it is copyleft, not a permissive "do anything with proprietary derivatives"
  license;
- binary source-delivery and notice processes become permanent release duties.

This is the lowest engineering-risk route to a compliant `1.0.0` with the
current code and dependencies.

### Route B: purchase an appropriate commercial PyQt license

Advantages:

- retains current PyQt6 code with minimal migration risk;
- allows a GPL-incompatible application license, subject to the purchased
  agreement;
- could support a permissive or proprietary application licensing strategy.

Trade-offs:

- recurring or version-dependent cost and vendor terms require direct review;
- does not automatically remove all Qt and third-party notice obligations;
- the exact right to redistribute current and future builds depends on the
  commercial agreement, not assumptions in this repository.

### Route C: migrate away from PyQt6, for example to an LGPL binding

Advantages:

- can enable a permissive application license without purchasing PyQt;
- removes the GPL-only PyQt binding constraint;
- may better match the stated intention to allow proprietary derivatives.

Trade-offs:

- broad import, behavior, packaging, and regression work before `1.0.0`;
- LGPL replacement/relinking requirements still affect binary layout;
- the replacement binding and every packaged module need a fresh bottom-up
  audit;
- creates schedule and UI-regression risk in an otherwise finished desktop
  application.

## Recommendation

If the priority is a stable and compliant `1.0.0` without reopening the Qt UI,
select GPL-3.0-only and keep community PyQt6. It permits commercial use and
modification but requires redistributed derivatives to remain open.

If the non-negotiable goal is a genuinely permissive application license such
as Apache-2.0 or MIT, do not label the current PyQt6 build permissive. Choose a
commercial PyQt agreement or complete a binding migration first. Of those two,
the commercial license has lower engineering risk; migration has lower direct
license cost but much higher development and regression cost.

## Separate attribution and brand documents

After the application-license route is selected, create:

- a short trademark/branding policy defining which builds may use the official
  name, icon, and "official" designation;
- a non-binding creator guideline requesting visible or spoken credit when the
  application is used to produce shows, streams, or videos;
- an optional product proposal for embedding "Made with Akihabarai Score" in
  exported images, which must not be implemented as a hidden licensing
  condition.

These documents must not contradict the permissions of the selected software
license.
