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

Keep the baseline dataset unchanged. Create an isolated learner copy:

```bash
python -m rules_purpose.exercise init --case matrix-02 --file exercises/return-format.json
python -m rules_purpose demo --exercise exercises/return-format.json --out reports/exercise-before
```

Open `exercises/return-format.json`. In `case.candidate`, wrap the existing useful answer in the required JSON fields. For this exact exercise, replace that field with:

```json
"candidate": "{\"reply\": \"Your unused lamp is within the 30-day return window. Please provide your order number so support can help start a return request.\", \"action\": \"request_details\", \"policy_ids\": [\"P1\"]}"
```

Keep the surrounding file valid JSON. Evaluate the changed copy:

```bash
python -m rules_purpose demo --exercise exercises/return-format.json --out reports/exercise-stale
```

**Expected: Review.** The contract now passes, but the original assessment belongs to the old plain-text candidate. Its quotations still match; its input fingerprint does not. An evaluation run never silently refreshes that fingerprint.

Review all three scores, quotations, and reasons against the current customer, candidate, policy, and rubric. In this formatting-only repair, the semantic assessment remains applicable. Record your completed reassessment with a meaningful note:

```bash
python -m rules_purpose.exercise reassess --file exercises/return-format.json --note "Reviewed all three dimensions: only the JSON wrapper changed; the advice, scores, and excerpts remain supported."
python -m rules_purpose demo --exercise exercises/return-format.json --out reports/exercise-after
python -m pytest -q
```

**Expected: the exercise is Eligible and baseline tests still pass.** The original `matrix-02` stays blocked, preserving the four-quadrant demonstration. There is no `expected` field to change in a learner copy.

The reassessment command validates scores and excerpts and records your note with the new input binding. It does not perform semantic grading, change scores, prove you reviewed anything, or grant release approval. A fingerprint is an integrity aid, not authority. If you change the advice, review and edit the assessment before recording reassessment. Never refresh a fingerprint just to get green.

**Optional extension:** create a second copy of `matrix-01`, replace the irrelevant catalog advice, and revise the assessment with defensible evidence. Have another participant review it. Learner files live in the ignored `exercises/` directory; commands refuse to overwrite existing exercises or write into baseline files. Held-out cases are not exercise templates.

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
