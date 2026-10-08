"""Create learner copies and explicitly record reassessment; never edit baseline data."""
import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path

from .core import (ROOT, read_json, strict_json, assessment_errors,
                   assessment_input_fingerprint)


def exercise_path(filename):
    path = Path(filename).resolve()
    if path.is_relative_to(ROOT) and not path.is_relative_to(ROOT / 'exercises'):
        raise ValueError('Inside this repository, learner files must be under exercises/; baseline files are protected')
    return path


def load_exercise(filename):
    path = exercise_path(filename)
    value = strict_json(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict) or value.get('version') != 'exercise-v1':
        raise ValueError('Expected an exercise-v1 learner file')
    case = value.get('case')
    if not isinstance(case, dict) or not all(isinstance(case.get(k), str) and case[k].strip()
                                          for k in ('id', 'customer', 'requirement', 'candidate')):
        raise ValueError('Exercise needs nonblank id, customer, requirement, and candidate strings')
    if case.get('split') != 'exercise' or 'simulated_judge' in case or 'expected' in case:
        raise ValueError('Learner cases must use the exercise split, without baseline expectations or simulated judges')
    # Missing/invalid assessments remain loadable: the gate must report Review.
    case.setdefault('assessment', None)
    return value


def initialize(case_id, filename):
    path = exercise_path(filename)
    cases = read_json(ROOT / 'data/scenarios.json')['cases']
    matches = [c for c in cases if c['id'] == case_id and c['split'] == 'dev']
    if not matches:
        raise ValueError('Choose a development scenario ID; held-out cases are not exercise templates')
    case = copy.deepcopy(matches[0])
    case.pop('expected')
    case.pop('simulated_judge', None)
    case['split'] = 'exercise'
    value = {'version': 'exercise-v1', 'origin_scenario_id': case_id,
             'assessment_provenance': 'Copied authored fixture; not yet reassessed by the learner',
             'review_history': [], 'case': case}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as output:
        output.write(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    return path


def reassess(filename, note):
    if not note.strip():
        raise ValueError('A nonblank reassessment note is required')
    path = exercise_path(filename)
    value = load_exercise(path)
    case = value['case']
    policy = read_json(ROOT / 'data/policy.json')
    rubric = read_json(ROOT / 'data/rubric.json')
    assessment = copy.deepcopy(case.get('assessment'))
    if not isinstance(assessment, dict):
        raise ValueError('Edit the assessment scores and evidence before recording reassessment')
    binding = assessment_input_fingerprint(case, case['candidate'], policy, rubric)
    old_binding = assessment.get('input_fingerprint')
    assessment['input_fingerprint'] = binding
    errors = assessment_errors(assessment, case['candidate'], policy, expected_fingerprint=binding)
    if errors:
        raise ValueError('Reassessment cannot be recorded: ' + '; '.join(errors))
    history = value.get('review_history')
    if not isinstance(history, list):
        raise ValueError('Exercise review_history must be a list')
    history.append({'recorded_at': datetime.now(timezone.utc).isoformat(), 'note': note.strip(),
                    'previous_input_fingerprint': old_binding, 'input_fingerprint': binding})
    case['assessment'] = assessment
    value['assessment_provenance'] = 'Learner-declared reassessment; identity and semantic correctness are not independently verified'
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init', help='Copy one development fixture without overwriting existing work')
    init.add_argument('--case', required=True)
    init.add_argument('--file', required=True)
    review = sub.add_parser('reassess', help='After reviewing scores/evidence, bind them to current inputs')
    review.add_argument('--file', required=True)
    review.add_argument('--note', required=True, help='Explain your completed reassessment; does not automatically grade')
    args = parser.parse_args(argv)
    try:
        path = initialize(args.case, args.file) if args.command == 'init' else reassess(args.file, args.note)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f'{args.command}: {path}')
    if args.command == 'reassess':
        print('Recorded your stated reassessment. No automated semantic grading or release approval occurred.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
