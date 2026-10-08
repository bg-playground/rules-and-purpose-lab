# v0.1 scope and acceptance

**Objective:** a newcomer can run the lab without credentials, explain the two evidence layers, and trace a release decision to a specific scenario.

| Acceptance | Evidence |
| --- | --- |
| Four contract/purpose combinations on one customer need | `matrix-01` through `matrix-04`; quadrant acceptance test |
| At least 12 fictional scenarios with separate holdout | 16 scenarios: 12 development / 4 holdout; selection tests |
| Deterministic checks fail safely on malformed/wrong-type output | Contract boundary tests |
| Purpose criteria are explicit and independently visible | Versioned rubric, evidence report |
| Existing citations do not imply semantic grounding | `dev-12` and policy-misuse test |
| Grader can be challenged; disagreement does not auto-approve | `dev-09`, simulated/reference evidence, calibration tests |
| Missing/malformed grading or provider failure cannot approve | Evidence and adapter failure tests |
| Both offline and optional live paths exist | Offline CLI tests; mocked live/provider tests |
| Live candidates never inherit fixture assessments | Generation/grading payload tests |
| Repeat runs preserve individual outcomes | Per-trial records and aggregate failure tests |
| Reports expose requirement, observation, checks, assessment, decision, provenance | JSON/Markdown report and example |
| CI tests the harness, including expected bad-candidate rejection | GitHub Actions workflow; no API credentials |
| A short applied teaching path exists | Five-minute guide and 20-minute workshop |

## Verification boundaries

Automated verification covers the offline acceptance behavior and mocked live transport/error paths. A credentialed live run must be separately observed before claiming provider-backed results. Authored fixture assessments are not independently validated semantic ground truth.

The checked-in example is generated from the four matrix cases and `dev-09`. Its revision/dirty state describe the source checkout at generation; it is an illustration, not CI or live evidence. Fresh CI reports are attached to each workflow run.

## Deliberately outside v0.1

Web dashboard, multiple providers, real customer integrations, benchmark claims, automated human-review resolution, production deployment, BGSTM/NAT integrations, and paid hosting. Add them only when a concrete teaching or adoption need justifies their cost.

## v0.2 bounded increment: evidence integrity and learner experience

| Acceptance | Evidence |
| --- | --- |
| Old quotes cannot approve a modified candidate | Regression appends a false refund claim while preserving every prior quote; outcome Review |
| Assessments bind every meaning-bearing input | Candidate, scenario ID, customer, requirement, policy, and rubric mutation tests |
| Missing/invalid binding and stale calibration reference fail closed | Binding and reference regression cases |
| Live binding belongs to actual submitted inputs | Mocked live generator/judge tests; model cannot provide its own binding |
| Learners can repair a candidate without weakening baseline acceptance | Complete copy → repair → Review → explicit reassessment → Eligible exercise test; original remains Block |
| Exercise tooling protects baseline and existing work | Protected-path, exclusive-create, and held-out-template tests |
| Reports distinguish validity from high scores | Stale evidence displays Not Established; disagreements display Disputed with both reasons |
| Technical evidence remains inspectable | JSON unchanged in purpose; expandable Markdown evidence and provenance |

The original 16 scenario outcomes remain 8 Block / 1 Review / 7 Eligible. v0.2 does not add comparison tooling, live model runs, independent human validation, or deployment. Existing fixture labels were preserved and bound to their current inputs; this migration does not claim fresh semantic validation.
