# Contracts and rubrics

The application returns exactly `reply`, `action`, and `policy_ids`. The customer-facing reply is a draft: no refunds, order lookups, account changes, or other external actions occur.

## Contract v1

| ID | Mechanically checked | Does not establish |
| --- | --- | --- |
| C1 | Strict JSON object; rejects duplicate keys and non-finite constants | Meaning or usefulness |
| C2 | Exactly the three required fields | That the fields contain correct advice |
| C3 | Nonblank string reply, at most 1200 characters | Clarity, completeness, or tone |
| C4 | Action is request_details, escalate, explain_policy, or check_shipment | That the action fits this customer |
| C5 | Nonempty list of unique, existing policy IDs | That those policies support the response |

When C1 fails, dependent checks are not attempted. A plain-text answer can still have meaningful purpose evidence, so the two layers remain visible.

## Rubric v1

The canonical anchors are in [data/rubric.json](../data/rubric.json).

| Dimension | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Relevance | Misses the actual request | Partially addresses it | Addresses material concerns |
| Grounding | Contradiction, invented fact, or claimed execution | Unsupported or ambiguous implication | Supported claims with uncertainty preserved |
| Actionability | No useful, feasible, safe next step | Vague or incomplete next step | Clear next step with necessary details |

Each dimension must reach 2 for eligibility. This intentionally strict teaching threshold is not empirically calibrated for production. No averaging is used.

Every assessment includes exact candidate and policy excerpts plus a brief reason. Code verifies the excerpts exist. Code cannot establish that the excerpts justify the score. The `dev-09` exercise intentionally gives a mistaken simulated judge authentic excerpts and invalid conclusions.

## Where grades come from

- **demo:** versioned, AI-assisted authored fixture assessments. No fresh grading occurs.
- **calibrate:** a live model grades existing fixture candidates; the gate detects threshold-classification disagreement with reference fixtures. References are not exposed to the judge.
- **live:** a live model grades a newly generated candidate. The original fixture assessment is not applicable and is not used. No independent reviewer is implied.

The application does not let a judge submit its own release decision. The grade schema rejects extra fields; a separate code-based gate decides. Separating the gate does not eliminate grader bias or make the judgment independent.
