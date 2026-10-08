"""Contract checks, evidence validation, and a fail-closed release policy."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIMENSIONS = ("relevance", "grounding", "actionability")
ACTIONS = {"request_details", "escalate", "explain_policy", "check_shipment"}
VERSIONS = {"contract": "contract-v1", "gate": "gate-v2", "dataset": "dataset-v2", "assessment_binding": "binding-v1"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")).encode()).hexdigest()


def assessment_input_fingerprint(case, raw, policy, rubric):
    """Bind meaning-bearing inputs, not scores, expected outcomes, or split labels."""
    return fingerprint({"binding_version": "binding-v1", "scenario_id": case["id"],
                        "customer": case["customer"], "requirement": case["requirement"],
                        "candidate": raw, "policy": policy, "rubric": rubric})


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = value
        return result

    def invalid_constant(_):
        raise ValueError("Non-finite JSON constant")

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid_constant)


def contracts(raw, policy):
    try:
        obj = strict_json(raw)
    except (ValueError, TypeError):
        return [{"id": "C1", "pass": False, "detail": "Valid strict JSON object required"}]
    checks = [("C1", isinstance(obj, dict), "JSON object")]
    if not isinstance(obj, dict):
        return [dict(id=i, **{"pass": ok}, detail=d) for i, ok, d in checks]
    checks += [
        ("C2", set(obj) == {"reply", "action", "policy_ids"}, "Exact required fields"),
        ("C3", isinstance(obj.get("reply"), str) and 0 < len(obj["reply"].strip())
         and len(obj["reply"]) <= 1200, "Nonblank reply, at most 1200 characters"),
        ("C4", isinstance(obj.get("action"), str) and obj["action"] in ACTIONS,
         "Allowed action enum"),
        ("C5", isinstance(obj.get("policy_ids"), list) and len(obj["policy_ids"]) > 0
         and all(isinstance(p, str) and p in policy["rules"] for p in obj["policy_ids"])
         and len(set(obj["policy_ids"])) == len(obj["policy_ids"]),
         "Nonempty, unique, existing policy IDs"),
    ]
    return [dict(id=i, **{"pass": bool(ok)}, detail=d) for i, ok, d in checks]


def assessment_errors(assessment, raw, policy, *, expected_fingerprint=None):
    """Presence/exact-quote checks establish provenance, not semantic truth."""
    if not isinstance(assessment, dict) or set(assessment) != {"scores", "evidence", "input_fingerprint"}:
        return ["Assessment requires scores, evidence, and input_fingerprint"]
    scores, evidence = assessment["scores"], assessment["evidence"]
    if not isinstance(scores, dict) or set(scores) != set(DIMENSIONS):
        return ["Incomplete score dimensions"]
    if not isinstance(evidence, dict) or set(evidence) != set(DIMENSIONS):
        return ["Incomplete evidence dimensions"]
    errors = []
    binding = assessment["input_fingerprint"]
    if not isinstance(binding, str) or len(binding) != 64 or any(c not in "0123456789abcdef" for c in binding):
        errors.append("Assessment input binding is missing or malformed")
    elif expected_fingerprint is not None and binding != expected_fingerprint:
        errors.append("Stale assessment: evaluated inputs changed; reassessment required")
    for dimension in DIMENSIONS:
        if type(scores[dimension]) is not int or scores[dimension] not in (0, 1, 2):
            errors.append(f"{dimension}: score must be integer 0..2")
        entry = evidence[dimension]
        required = {"candidate_quote", "policy_id", "policy_quote", "reason"}
        if not isinstance(entry, dict) or set(entry) != required or not all(
            isinstance(v, str) and v.strip() for v in entry.values()
        ):
            errors.append(f"{dimension}: incomplete evidence")
            continue
        if entry["candidate_quote"] not in raw:
            errors.append(f"{dimension}: candidate quote not found")
        if entry["policy_id"] not in policy["rules"] or entry["policy_quote"] not in policy["rules"].get(entry["policy_id"], ""):
            errors.append(f"{dimension}: policy quote not found")
    return errors


def purpose_pass(assessment, rubric):
    return all(assessment["scores"][d] >= rubric["thresholds"][d] for d in DIMENSIONS)


def decide(checks, assessment, errors, rubric, *, disagreement=False):
    # Known hard failures block even if a grader is unavailable.
    if any(not c["pass"] for c in checks):
        return {"status": "BLOCK", "reason": "Mandatory output contract failed"}
    if not checks or errors or assessment is None:
        return {"status": "REVIEW", "reason": "Required evaluation evidence is missing or invalid"}
    # A conflicting assessment does not silently overrule either side.
    if disagreement:
        return {"status": "REVIEW", "reason": "Material grader/reference disagreement"}
    if not purpose_pass(assessment, rubric):
        return {"status": "BLOCK", "reason": "A purpose dimension is below its threshold"}
    return {"status": "ELIGIBLE", "reason": "Meets this lab's criteria for the evaluated scenario"}


def aggregate(records):
    statuses = {r["decision"]["status"] for r in records}
    return "BLOCK" if "BLOCK" in statuses else "REVIEW" if not records or "REVIEW" in statuses else "ELIGIBLE"


def evaluate(case, raw, assessment, policy, rubric, *, reference=None, source="authored_fixture"):
    checks = contracts(raw, policy)
    input_fingerprint = assessment_input_fingerprint(case, raw, policy, rubric)
    errors = assessment_errors(assessment, raw, policy, expected_fingerprint=input_fingerprint)
    disagreement = False
    if reference is not None:
        ref_errors = assessment_errors(reference, raw, policy, expected_fingerprint=input_fingerprint)
        errors += ["Reference: " + e for e in ref_errors]
        if not errors:
            disagreement = any((assessment["scores"][d] >= rubric["thresholds"][d]) !=
                               (reference["scores"][d] >= rubric["thresholds"][d]) for d in DIMENSIONS)
    return {
        "scenario_id": case["id"], "split": case["split"], "customer": case["customer"],
        "requirement": case["requirement"], "candidate": raw,
        "input_fingerprint": input_fingerprint,
        "assessment_source": source, "contracts": checks, "assessment": assessment,
        "assessment_errors": errors, "reference": reference, "disagreement": disagreement,
        "decision": decide(checks, assessment, errors, rubric, disagreement=disagreement),
    }
