# Optional live evaluation

Offline mode is the default teaching path. Live mode makes paid requests to OpenAI's Responses API using a user-provided `OPENAI_API_KEY`. It sends only fictional case data, policy, prompts, rubric, and candidates. No live requests are made by GitHub Actions.

## Configure and start small

Choose available generator and judge model IDs. Prefer stable model snapshots where available, and a different judge when practical. Different model names do not establish independent validation.

macOS/Linux:

```bash
export OPENAI_API_KEY='your-key'
```

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY = 'your-key'
```

Do not commit the key. `.env` files are ignored but not automatically loaded. No credentials are written by the report generator. Raw provider error bodies and authorization headers are not included in reports.

```bash
python -m rules_purpose calibrate --judge-model YOUR_JUDGE_MODEL --case dev-09 --out reports/calibration-01
python -m rules_purpose live --model YOUR_GENERATOR_MODEL --judge-model YOUR_JUDGE_MODEL --case matrix-04 --repeat 3 --out reports/live-01
```

`calibrate` uses one judge request per case/trial. `live` uses one generation and one judge request per successful case/trial. Thus 16 cases × 3 trials can use 96 requests. Repetition is bounded at 5; there are no automatic retries. Each request has a 60-second network timeout and a 3000-output-token ceiling. These are bounded lab defaults, not token/cost optimization claims.

## What is retained

The report stores prompts and their fingerprints, policy/rubric snapshots, dataset fingerprint, code commit/dirty state, requested and returned model IDs, provider response IDs, token usage if available, raw candidates and judge text, parsed evidence, and run time. Reasoning internals are neither requested nor saved.

Requests set `store: false`; this does not make a broader claim about provider retention policies. The endpoint is fixed to the documented OpenAI API. A network/API failure is reported as unavailable evidence, not graded as a bad answer. A known malformed candidate still blocks if its judge later fails.

## Grade the grader before relying on it

Calibration compares threshold classifications on fixed candidates against authored references. It reports disagreements; it does not prove grader reliability. Review individual reasons, especially incorrect approval, not just totals. For production, replace or supplement these authored labels with independently reviewed domain examples and quantify agreement on a larger held-out set.

The judge never sees fixture scores or expected decisions. In live mode, the generator sees only policy and customer text. The judge sees policy, customer text, rubric, and the actual generated candidate. Neither model supplies the final release decision.

The adapter requests plain text JSON and validates it locally. Invalid JSON, missing fields, invalid scores, fabricated quotations, incomplete provider output, or refusal without usable text cannot create eligibility. No automatic repair silently converts a failed response into a passing one.

## Variability and held-out cases

```bash
python -m rules_purpose live --model YOUR_GENERATOR_MODEL --judge-model YOUR_JUDGE_MODEL --split holdout --repeat 3 --out reports/holdout-live-01
```

Inspect each trial; one failing trial cannot be averaged away. Repeated live runs are observations of variability, not a statistical reliability claim. Provider behavior and aliases can change. Keep the original report when comparing runs and use unique output directories.

Known limitation: live mode uses model-based purpose judgments without an independent human sign-off workflow. `ELIGIBLE` is a local criteria result, not release authorization. An external production process would still need calibrated risk policy, broader evidence, and appropriate accountable approval.
