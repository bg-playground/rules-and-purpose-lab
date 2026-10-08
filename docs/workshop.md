# A 20-minute workshop: rules, purpose, and release evidence

**Audience:** QA engineers, developers, product owners, and business analysts.

**Preparation:** Python 3.11+ and a repository checkout. No key, paid service, dashboard, or customer data needed. Read only development cases until the final exercise.

**Outcomes:** distinguish contract checks from purpose judgments; trace a decision to evidence; explain grader uncertainty; avoid equating green CI with model quality.

## Minutes 0–3: predict

Read the four candidates in the README. Individually predict the contract result, purpose result, and release decision. Ask: “What does the customer actually need?” Then compare predictions with a partner.

## Minutes 3–7: run and inspect

```bash
python -m rules_purpose demo --case matrix-01 --case matrix-02 --case matrix-03 --case matrix-04 --out reports/workshop-start
```

Open `reports/workshop-start/report.md`. Find a useful answer that fails integration. Find valid JSON that misses the task. Identify exactly which evidence supports each conclusion.

**Discussion:** What would a JSON-only test suite miss? What would a helpfulness-only grader miss?

## Minutes 7–12: repair one layer at a time

Work on a local branch. Edit [data/scenarios.json](../data/scenarios.json).

1. For `matrix-02`, wrap the useful answer in the required JSON fields. Preserve its meaning. Make `candidate_quote` values exact substrings of the new raw candidate. Re-run that single case.
2. For `matrix-01`, replace the catalog advice with a useful, policy-supported return response. Review all three rubric dimensions. Update the authored assessment and its evidence only after explaining your reasoning; do not merely raise scores to get green.
3. Update the fixtures' `expected` values only when justified by the new evidence. Run pytest. In a collaborative workshop, ask another person to review your edits.

Because demo mode replays fixture assessments, changing only the candidate does **not** create a fresh semantic grade. Stale quotations should trigger Review. Even if old quotations still match, their meaning must be reassessed. This is an intentional lesson about maintaining evaluation data.

## Minutes 12–16: challenge the judge

```bash
python -m rules_purpose demo --case dev-09 --out reports/disagreement
```

The customer is 45 days past delivery. The response promises a refund and guarantees approval. The simulated judge gives maximum scores; the reference assessment disagrees.

- Are the judge's quotations real?
- Does its explanation follow from the 30-day policy?
- Why is confidence not evidence?
- Why is Review appropriate for disputed judgment?

The simulated judge is explicitly fictional. To observe actual grader behavior, the optional `calibrate` command grades the same candidate with a configured model. It might agree with the reference; a live disagreement is not guaranteed.

## Minutes 16–20: evaluate transfer

Before opening holdout cases, write your expected behavior for delivery ages 30 and 31 days and contradictory statements about product use.

```bash
python -m rules_purpose demo --split holdout --out reports/holdout
```

Compare your predictions with the authored evidence. These four cases are teaching checks of your reasoning, not fresh measurements of a model. Use `live --split holdout` for fresh outputs after freezing the prompt, rubric, and gate.

Once a held-out case has influenced an edit, it is development data for that exercise. Add new unseen cases for the next evaluation.

## Facilitator answer guide

- Four quadrants: Block, Block, Block, Eligible.
- `dev-09`: Review because purpose threshold classifications conflict.
- At most 30 days includes day 30. Day 31 requires explaining the standard limit and offering review without promising an exception.
- Contradictory condition statements require clarification.
- Green lab CI means expected decisions were produced, including expected blocks. It does not mean the candidates are all good.

**Exit ticket:** In one paragraph, explain what a release report establishes, what it leaves uncertain, and what evidence you would add for a real deployment.
