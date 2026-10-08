# Release policy v1

Decisions apply to the evaluated candidate and scenario. They do not certify a product, deployment, or general model capability. No command deploys anything.

## Decision precedence

| Priority | Evidence | Decision |
| --- | --- | --- |
| 1 | Any observed mandatory contract failure | BLOCK |
| 2 | Candidate unavailable, absent checks, or missing/invalid purpose evidence | REVIEW |
| 3 | In calibration, a material disagreement with the authored reference | REVIEW |
| 4 | Any valid purpose score below its dimension threshold | BLOCK |
| 5 | All required evidence present and criteria satisfied | ELIGIBLE |

A known contract failure remains a block even when grading is unavailable. A disputed semantic judgment goes to review, so the gate does not silently accept either grader as authority. Material disagreement means at least one dimension crosses its pass/fail threshold; a difference between 0 and 1 alone does not cross the threshold, but remains visible in the report.

For multiple cases/trials: any Block blocks the run; otherwise any Review requires review; otherwise all records must be Eligible. An empty run cannot pass. There is no majority vote or mean score that masks a failed trial.

## Worked decisions

- `matrix-02`: useful plain text → contract failure → Block.
- `dev-12`: valid JSON with a real policy ID but fabricated execution → purpose failure → Block.
- `dev-09`: simulated judge says eligible; authored reference identifies a promised exception → Review.
- `matrix-04`: correct structure and sufficient fixture assessment → Eligible **for that fixture**.
- Provider unavailable before generation → no observed candidate → Review.

## Exit codes

| Mode | 0 | 1 | 2 |
| --- | --- | --- | --- |
| demo | Demonstration completed, regardless of candidate outcomes | Unexpected runtime failure may use a nonzero exit | Invalid CLI configuration |
| live / calibrate | Evaluated run is Eligible | Evaluated run is Block | Evaluated run needs Review, or CLI configuration is invalid |

A completed evaluation writes a report. CLI validation errors exit before evaluation and may not produce one; use a fresh `--out` directory to avoid mistaking an older report for a new run. Local filesystem/programming errors propagate rather than pretending a valid run occurred.

CI executes offline acceptance tests and generates a demo report. It verifies the **lab**, not a live model. Intentionally blocked fixture candidates must not make a correct lab's CI red.

## Handling review

The report preserves the disagreement and evidence. A learner/reviewer should record which policy applies, why a score is defensible, and whether the rubric needs revision. Change the versioned fixtures/rubric through code review and rerun relevant cases. There is deliberately no automatic override or self-approval button. If the exercise calls for human validation, an actual person must perform and record it; the fixture labels are not a substitute.
