# Limits and responsible interpretation

This is an educational application of quality reasoning, not a production support product or a general AI benchmark.

- **Small synthetic dataset:** 16 deliberately selected cases, 12 development and four held-out teaching cases. No coverage or accuracy percentage should be generalized beyond these examples.
- **Authored reference assessments:** AI-assisted fixture labels are editorial judgments. They have not been independently validated by customer-support experts. No human agreement statistic is claimed.
- **Public holdout:** a learning discipline, not protection against training contamination or benchmark leakage. Reading/tuning against a held-out case consumes its holdout status.
- **Judge uncertainty:** quoted evidence can be authentic while conclusions are wrong. Different generator/judge models can share biases. The simulated disagreement exists to teach this failure.
- **Contract scope:** schema checks establish only their specified rules. For example, they do not mechanically verify action appropriateness, policy applicability, privacy language, or task completion. Purpose evaluation addresses some of these, imperfectly.
- **No external actions:** the assistant drafts a response and recommends an action. It cannot perform a refund or inspect a shipment. There is no end-to-end verification of a real support system.
- **No deployment authority:** Eligible applies only to evaluated evidence and criteria. Passing a few cases does not authorize production deployment.
- **Live variability:** small repeats expose some inconsistency; they do not establish a confidence interval, calibrated error rate, or SLA. There is no retry-until-green logic.
- **Input trust:** prompts separate instructions from untrusted customer/candidate content, but prompting is not a robust security boundary. The injection fixture is an example, not a comprehensive attack suite.
- **Provenance:** fingerprints support comparison, not signatures or immutable audit storage. A dirty tree is disclosed; the commit alone does not identify uncommitted source code. Reports can be edited.

Before adapting this to production: gather representative real failure cases with appropriate data handling, obtain independent domain review, calibrate graders and thresholds, broaden deterministic checks where business rules allow, preserve protected evaluation sets, measure repeatability/cost, and connect decisions to an accountable release process.

Contribute a new scenario by stating the customer purpose, applicable requirement, candidate output, exact evidence, anchored assessment, split, and expected decision. Validate both the label's reasoning and the harness behavior. Never change a label solely to make CI green.
