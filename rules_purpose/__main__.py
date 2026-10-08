"""python -m rules_purpose demo | live | calibrate"""
import argparse
import os
import subprocess
from datetime import datetime, timezone

from .core import (ROOT, VERSIONS, read_json, fingerprint, strict_json, evaluate,
                   aggregate, assessment_errors, contracts, decide)
from .provider import respond, ProviderError
from .report import write_report


def run_live(case, policy, rubric, generate_prompt, judge_prompt, model, judge_model,
             api_key, *, calibrate=False, call=respond):
    trace = {}
    raw = case['candidate'] if calibrate else None
    assessment = None
    reference = case['assessment'] if calibrate else None
    error = None
    try:
        if not calibrate:
            raw, trace['generation'] = call(model, generate_prompt,
                                          {'policy':policy, 'customer':case['customer']}, api_key)
        judge_payload = {'customer':case['customer'], 'policy':policy,
                         'rubric':rubric, 'candidate':raw}
        judge_raw, trace['judge'] = call(judge_model, judge_prompt, judge_payload, api_key)
        trace['judge_raw'] = judge_raw
        try:
            assessment = strict_json(judge_raw)
        except (TypeError, ValueError):
            error = 'Judge returned invalid strict JSON'
    except ProviderError as exc:
        error = str(exc)
    if raw is None:
        record = {'scenario_id':case['id'], 'split':case['split'], 'customer':case['customer'],
                  'requirement':case['requirement'], 'candidate':None, 'contracts':[],
                  'assessment':None, 'assessment_source':'live_model', 'assessment_errors':[error],
                  'reference':reference, 'disagreement':False,
                  'decision':{'status':'REVIEW','reason':'Candidate generation unavailable'}}
    else:
        record = evaluate(case, raw, assessment, policy, rubric, reference=reference, source='live_model')
        if error:
            record['assessment_errors'].append(error)
            record['decision'] = decide(record['contracts'], assessment, record['assessment_errors'], rubric,
                                        disagreement=record['disagreement'])
    record['provider_trace'] = trace
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('demo','live','calibrate'))
    parser.add_argument('--split', choices=('dev','holdout','all'), default='dev')
    parser.add_argument('--case', action='append', help='Select an ID; repeat for multiple cases. Still filtered by --split.')
    parser.add_argument('--repeat', type=int, default=1, help='Live/calibration trials, 1..5; no automatic retries')
    parser.add_argument('--model', help='Generator model ID; choose one available to your account')
    parser.add_argument('--judge-model', help='Judge model ID; a separate model is preferable but not independent validation')
    parser.add_argument('--out', default='reports/latest')
    args = parser.parse_args(argv)
    if not 1 <= args.repeat <= 5:
        parser.error('--repeat must be between 1 and 5')
    if args.mode == 'demo' and args.repeat != 1:
        parser.error('Repeating authored fixtures does not measure model variability')
    if args.mode != 'demo' and (not args.judge_model or (args.mode == 'live' and not args.model)):
        parser.error('Live mode needs --model and --judge-model; calibrate needs --judge-model')
    key = os.environ.get('OPENAI_API_KEY', '')
    if args.mode != 'demo' and not key:
        parser.error('Set OPENAI_API_KEY for paid API calls; demo needs no key')
    policy = read_json(ROOT/'data/policy.json')
    rubric = read_json(ROOT/'data/rubric.json')
    dataset = read_json(ROOT/'data/scenarios.json')
    cases = [c for c in dataset['cases'] if args.split == 'all' or c['split'] == args.split]
    if args.case:
        unknown = set(args.case) - {c['id'] for c in cases}
        if unknown:
            parser.error('Unknown IDs in selected split: ' + ', '.join(sorted(unknown)))
        cases = [c for c in cases if c['id'] in args.case]
    if not cases:
        parser.error('No scenarios selected')
    prompts = {name:(ROOT/f'prompts/{name}.txt').read_text(encoding='utf-8') for name in ('generate','judge')}
    records = []
    for case in cases:
        for trial in range(1, args.repeat+1):
            if args.mode == 'demo':
                simulated = case.get('simulated_judge')
                record = evaluate(case,case['candidate'],simulated or case['assessment'],policy,rubric,
                                  reference=case['assessment'] if simulated else None,
                                  source='simulated_judge_fixture' if simulated else 'authored_fixture')
            else:
                record = run_live(case,policy,rubric,prompts['generate'],prompts['judge'],
                                  args.model,args.judge_model,key,calibrate=args.mode == 'calibrate')
            record['trial'] = trial
            records.append(record)
    try:
        revision = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=normal'],cwd=ROOT,text=True))
    except (OSError, subprocess.CalledProcessError):
        revision, dirty = None, None
    offline = args.mode == 'demo'
    interpretation = ('Offline replay of authored teaching fixtures. Mixed candidates are intentionally blocked; this is not a release judgment on a model or on the lab. No live API calls occurred.' if offline else
                      'Live calibration against authored fixture assessments; these are not independent human labels. Outcome concerns this calibration run, not generator release.' if args.mode == 'calibrate' else
                      'Live candidate evaluation on the selected scenarios only. Eligible means this lab\'s criteria were met; it is not proof of production readiness or human approval.')
    report = {'mode':args.mode, 'outcome':aggregate(records), 'interpretation':interpretation,
              'provenance':{'versions':{**VERSIONS,'policy':policy['version'],'rubric':rubric['version']},
                            'dataset_provenance':dataset['assessment_provenance'],
                            'dataset_fingerprint':fingerprint(dataset),
                            'prompt_fingerprints':{k:fingerprint(v) for k,v in prompts.items()},
                            'prompts':prompts, 'code_revision':revision,'working_tree_dirty':dirty,
                            'created_at':None if offline else datetime.now(timezone.utc).isoformat(),
                            'split':args.split,'repeats':args.repeat,
                            'requested_generator':args.model if args.mode == 'live' else None,
                            'requested_judge':args.judge_model if not offline else None},
              'policy':policy,'rubric':rubric,'records':records}
    write_report(report,args.out)
    print(f"{args.mode}: {len(records)} records; {report['outcome']}. Report: {args.out}/report.md")
    # Demo success means the harness ran, NOT that the fictional candidates pass.
    return 0 if offline or report['outcome'] == 'ELIGIBLE' else 1 if report['outcome'] == 'BLOCK' else 2


if __name__ == '__main__':
    raise SystemExit(main())
