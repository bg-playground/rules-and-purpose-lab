# Rules & Purpose Lab

**Deterministic testing tells us whether the system obeyed a rule. AI evaluation helps us determine whether the result fulfilled its purpose. A trustworthy release process needs both.**

A small, runnable customer-support lab that turns this idea into inspectable release evidence. No API key is needed for the workshop. Python 3.11+; no runtime dependencies.

[![Lab acceptance](https://github.com/bg-playground/rules-and-purpose-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/bg-playground/rules-and-purpose-lab/actions/workflows/ci.yml)

**Start here:** [Five-minute example](docs/first-five-minutes.md) · [20-minute workshop](docs/workshop.md) · [Example evidence report](examples/report.md)

## One customer, four outcomes

> “My unused desk lamp arrived 10 days ago. I would like to return it. What should I do?”

| Candidate | Contract | Purpose | Decision |
| --- | --- | --- | --- |
| Valid JSON recommending the product catalog | Pass | Fail | Block |
| Helpful return instructions, but plain text instead of JSON | Fail | Pass | Block |
| Plain text claiming a refund and order deletion | Fail | Fail | Block |
| Valid JSON explaining eligibility and asking for the order number | Pass | Pass | Eligible for this scenario |

These are **authored teaching fixtures**, including AI-assisted assessments. They are not independent human validation, live model results, or measured model performance. The deliberate grader disagreement is also simulated and labeled.

## Run it

From a repository checkout:

```bash
git clone https://github.com/bg-playground/rules-and-purpose-lab.git
cd rules-and-purpose-lab
python -m rules_purpose demo
```

Open `reports/latest/report.md`. The default run contains 12 development cases; `--split all` includes four held-out teaching cases. The mixed fixture run reports **BLOCK** because it intentionally contains bad candidates. The command exits successfully because the demonstration ran successfully.

To see just the four contrasting outputs:

```bash
python -m rules_purpose demo --case matrix-01 --case matrix-02 --case matrix-03 --case matrix-04 --out reports/matrix
```

To verify the lab itself:

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q
```

On Windows, use `py` instead of `python` if that is how Python is installed.

## What the lab checks

- **Contracts:** strict JSON, exact fields, bounded nonblank reply, allowed action, and existing policy IDs.
- **Purpose:** relevance, grounding, and actionability, each scored against explicit anchors and supported with excerpts.
- **Decision:** block a known failure, review missing/conflicting evidence, or mark the evaluated candidate eligible under the lab's criteria.

Deterministic checks are one kind of evaluation. Purpose evidence can come from people, code, or models. This lab separates what is mechanically established from what requires semantic judgment; it does not claim that one replaces the other.

A policy ID can exist while the response misuses its policy. Exact quotations can be real while a grader's conclusion is wrong. These are explicit exercises here.

## Inspect the evidence

Each report includes the customer need, requirement, raw candidate, individual checks, rubric scores, quoted evidence, decision reason, policy/rubric snapshots, dataset and prompt fingerprints, and code revision/dirty state. Live runs additionally record returned model IDs, response IDs, token usage when provided, raw grader output, and UTC run time. Fingerprints identify inputs; they do not prove correctness or make live output deterministic.

The evidence chain is:

**Requirement → observed output → contract checks + purpose assessment → release decision.**

This is a small applied illustration of BGSTM's evidence-to-decision approach and NAT's emphasis on inspectable quality evidence. It does not depend on, integrate with, or certify either project.

## Optional live evaluation

The optional adapter uses OpenAI's Responses API. Choose model IDs available to your account. Set `OPENAI_API_KEY` in your shell; `.env` files are ignored by git but are **not automatically loaded**. Live commands make paid API calls. Start with one case.

```bash
python -m rules_purpose calibrate --judge-model YOUR_JUDGE_MODEL --case dev-09 --out reports/calibration
python -m rules_purpose live --model YOUR_GENERATOR_MODEL --judge-model YOUR_JUDGE_MODEL --case matrix-04 --repeat 3 --out reports/live
```

`calibrate` asks a real judge to assess a fixed candidate and compares pass/fail classifications with the authored fixture assessment. `live` generates new candidates, then grades them; it never reuses fixture grades for new outputs. See [Live mode](docs/live-mode.md) for provenance, repetition, exit codes, and limits.

No live calls run in CI. A green CI badge means the lab behaves as specified, including correctly rejecting bad candidates. It is not a model-quality badge.

## Learn, then challenge the design

| Resource | What it teaches |
| --- | --- |
| [Contracts and rubrics](docs/contracts-and-rubrics.md) | Exactly what each check can and cannot establish |
| [Release policy](docs/release-policy.md) | Decision precedence, no score averaging, and review states |
| [Workshop](docs/workshop.md) | Predict, run, inspect, repair, and challenge a grader |
| [Limitations](docs/limitations.md) | Coverage, calibration, variability, and production boundaries |
| [Acceptance and scope](docs/acceptance.md) | The bounded v0.1 deliverable and its verification |

The four holdout cases are public for teaching. Avoid inspecting/tuning against them during the exercise; once you do, treat them as development data. They are not a secret benchmark.

## References

- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — combining code, model, and human graders.
- [OpenAI: Text generation](https://developers.openai.com/api/docs/guides/text) — the Responses API used by the optional adapter.

All customer cases, order IDs, and company policies are fictional. No real customer data is required. This project has no open-source license grant yet; public visibility alone is not a license.
