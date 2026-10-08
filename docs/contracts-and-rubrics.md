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

## Assessment input binding v1 (added in v0.2)

Stored assessments now have three fields: `scores`, `evidence`, and `input_fingerprint`. The fingerprint covers binding version, scenario ID, exact raw candidate, customer message, requirement, full policy, and full rubric. It excludes scores, expected decisions, and the dev/exercise split; copying a fixture into a learner workspace does not itself change the evaluated meaning.

During every evaluation, the gate compares the stored fingerprint with the current inputs. Missing, malformed, or mismatched bindings cannot support eligibility. An existing contract failure still blocks; otherwise invalid evidence requires Review. Reference assessments in calibration must also match current inputs.

Live judges still return only scores and evidence. The harness assigns the binding immediately to the exact inputs it submitted, before validating the resulting evidence. The judge cannot supply or override it. The live judge also receives the scenario requirement. No fingerprint repair is performed during offline evaluation or calibration.

Authored fixture bindings were migrated once for v0.2 without changing the original labels. Learner reassessment is an explicit, note-bearing operation on a separate exercise file. Bindings detect stale input reuse, not dishonest label edits or semantic errors; independent review remains a distinct activity.
