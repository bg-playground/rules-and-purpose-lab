# Your first five minutes

**Learning objective:** explain why a valid response can be useless and a useful response can still break an integration.

1. Read the customer message in the README. The company allows unused-product returns within 30 days, needs an order number, and has not authorized the assistant to process refunds.
2. Predict which of the four candidates should be release-eligible. Write down your reasons before running the lab.
3. Run the four-case command below.
4. Open the generated Markdown report. Compare the contract results with relevance/grounding/actionability. Follow a policy quotation back to the policy at the end of the report.
5. Explain why `matrix-02` has maximum purpose scores but is still blocked.

```bash
python -m rules_purpose demo --case matrix-01 --case matrix-02 --case matrix-03 --case matrix-04 --out reports/first-five
```

The command prints `BLOCK`, yet exits with code 0. That is intentional: several fictional candidates are bad, but the demonstration completed. In CI, pytest verifies that these candidates are blocked for the expected reasons.

**Try one more:** `python -m rules_purpose demo --case dev-12 --out reports/policy-misuse`

Every contract check passes. The policy ID exists. The response nonetheless claims a refund has already been processed, which violates the cited policy. A mechanically valid citation is not semantic support.

The displayed grades in demo mode are authored fixtures. The program validates their shape and excerpts and applies the decision policy; it does not independently discover their semantic correctness.
