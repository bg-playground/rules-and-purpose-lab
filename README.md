![Rules & Purpose Lab — deterministic testing and AI evaluation. Teal and amber lenses examine the same sheet of paper.](assets/readme-hero.png)

# Rules & Purpose Lab

**Deterministic testing tells us whether the system obeyed a rule. AI evaluation helps us determine whether the result fulfilled its purpose. A trustworthy release process needs both.**

A small customer-support lab for QA engineers, developers, and business analysts. Run the examples, challenge the evidence, and explain the release decision.

[![Lab acceptance](https://github.com/bg-playground/rules-and-purpose-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/bg-playground/rules-and-purpose-lab/actions/workflows/ci.yml)

**Python 3.11+ · No runtime dependencies · No API key for the workshop**

[Five-minute introduction](docs/first-five-minutes.md) · [20-minute workshop](docs/workshop.md) · [Teaching deck](docs/presentation/Rules_and_Purpose_Lab_Teaching_Deck.pptx) · [Example report](examples/report.md)

## One customer, four outcomes

> “My unused desk lamp arrived 10 days ago. I would like to return it. What should I do?”

| Response | Contract | Purpose | Release decision |
| --- | --- | --- | --- |
| Valid JSON recommending the product catalog | Pass | Fail | **Block** |
| Helpful return instructions in plain text | Fail | Pass | **Block** |
| Plain text claiming a refund and order deletion | Fail | Fail | **Block** |
| Valid JSON with supported return instructions | Pass | Pass | **Eligible for this scenario** |

These are **AI-assisted authored teaching fixtures**. They are not independent human labels or measured model performance. The grader-disagreement example is also simulated and labeled.

## Try it in one minute

```bash
git clone https://github.com/bg-playground/rules-and-purpose-lab.git
cd rules-and-purpose-lab
python -m rules_purpose demo
```

Open `reports/latest/report.md`. The default run contains 12 development cases. Add `--split all` to include four held-out teaching cases.

**Why does a successful demo say BLOCK?** The dataset deliberately contains bad responses. The demo command exits successfully when it completes. CI verifies that the lab makes the expected decisions, including correctly blocking bad candidates.

On Windows, use `py` instead of `python` if that is how Python is installed.

## What you will learn

| Lesson | Applied example |
| --- | --- |
| Valid structure does not establish usefulness | An irrelevant response passes every contract check |
| Useful content can still break an integration | A helpful plain-text response fails the JSON contract |
| A valid citation can support an invalid conclusion | A response cites a real policy while inventing a completed refund |
| Evidence belongs to the exact evaluated inputs | Changing a response makes its old assessment stale, even when its quotations still match |
| Graders need scrutiny | A simulated confident judgment conflicts with the policy evidence |

Deterministic checks are one kind of evaluation. Code, people, and models can all contribute purpose evidence. The distinction here is between explicit contract compliance and evidence that an output fulfills its intended purpose.

## A release decision you can inspect

Every report connects the **requirement**, **observed response**, **contract checks**, and **purpose assessment** to a decision:

| Decision | Meaning |
| --- | --- |
| **Block** | A known contract failure or valid, uncontested purpose failure |
| **Review** | Missing, stale, or invalid evidence, or a material grading disagreement |
| **Eligible** | All required evidence and criteria pass for the evaluated scenario |

Known contract failures still block when a grader is unavailable. A high average never cancels a failing requirement. Eligibility under the lab's criteria does not authorize a production release.

Reports lead with the decision and its evidence. They withhold stale scores from the teaching summary and show disputed judgments side by side. Expand the technical sections for raw assessments, input fingerprints, policy/rubric snapshots, prompt versions, and run provenance.

[Read an example report](examples/report.md) · [Inspect the release policy](docs/release-policy.md)

## Repair a response without changing the baseline

```bash
python -m rules_purpose.exercise init --case matrix-02 --file exercises/return-format.json
python -m rules_purpose demo --exercise exercises/return-format.json --out reports/exercise-before
```

Follow the [workshop repair steps](docs/workshop.md) to edit the learner copy, observe a stale assessment, and record a defensible reassessment. The original examples and tests remain intact.

Input fingerprints detect stale assessments. They do not prove semantic correctness or reviewer identity. Evaluations never silently refresh them.

## Teach it with a short deck

The seven-slide presentation introduces the examples before the hands-on exercise. It includes editable tables and presenter notes with discussion prompts and source references.

**[Download the PowerPoint deck](docs/presentation/Rules_and_Purpose_Lab_Teaching_Deck.pptx)** · [Slide guide and facilitator notes](docs/presentation/README.md)

The next learning check is a small teaching trial: can someone unfamiliar with the lab complete the exercise and explain why contract compliance alone cannot establish release readiness?

## Verify the lab

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q
```

CI runs offline acceptance checks on Python 3.11, 3.12, and 3.13. It makes no paid API calls. The badge reflects lab behavior, not a model-quality benchmark.

## Optional live evaluation

Set `OPENAI_API_KEY` in your shell and choose model IDs available to your account. Live commands make paid requests through the OpenAI Responses API. Start with one case. `.env` files are ignored by git but are not automatically loaded.

```bash
python -m rules_purpose calibrate --judge-model YOUR_JUDGE_MODEL --case dev-09 --out reports/calibration
python -m rules_purpose live --model YOUR_GENERATOR_MODEL --judge-model YOUR_JUDGE_MODEL --case matrix-04 --repeat 3 --out reports/live
```

`calibrate` compares a live judge's classifications with authored fixture assessments. `live` generates and grades new responses without reusing fixture grades. The adapter has simulated-response test coverage; this project does not yet claim an observed provider-backed validation run.

[Live-mode guide](docs/live-mode.md)

## Explore the evidence and limits

| Resource | Purpose |
| --- | --- |
| [Contracts and rubrics](docs/contracts-and-rubrics.md) | What each check establishes and what remains judgment |
| [Release policy](docs/release-policy.md) | Decision precedence and review states |
| [Workshop](docs/workshop.md) | Predict, inspect, repair, and challenge a grader |
| [Acceptance and scope](docs/acceptance.md) | The v0.1 foundation and v0.2 evidence improvements |
| [Limitations](docs/limitations.md) | Dataset coverage, grader uncertainty, and production boundaries |
| [Visual assets](assets/README.md) | Illustration provenance and editable presentation information |

The four public holdout cases teach evaluation discipline. Once a case influences your changes, treat it as development data. They are not a secret benchmark.

This project illustrates BGSTM's evidence-to-decision approach and NAT's emphasis on inspectable quality evidence. It does not integrate with or certify either project.

## References

- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [OpenAI: Text generation](https://developers.openai.com/api/docs/guides/text)

All customer cases, order IDs, and company policies are fictional. No real customer data is required. The project has no open-source license grant yet; public visibility alone is not a license.
