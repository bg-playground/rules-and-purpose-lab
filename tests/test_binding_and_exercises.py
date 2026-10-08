"""Regressions for stale evidence and a complete learner repair without baseline edits."""
import copy
import json
from pathlib import Path

import pytest

from rules_purpose.core import ROOT, read_json, evaluate, assessment_input_fingerprint
from rules_purpose.__main__ import main, run_live
from rules_purpose.exercise import initialize, load_exercise, reassess
from rules_purpose.report import teaching_summary, markdown

POLICY = read_json(ROOT/'data/policy.json')
RUBRIC = read_json(ROOT/'data/rubric.json')
CASES = read_json(ROOT/'data/scenarios.json')['cases']
GOOD = CASES[3]


def test_appended_false_execution_claim_cannot_reuse_matching_quotes():
    obj = json.loads(GOOD['candidate'])
    obj['reply'] += ' Your refund has already been processed.'
    raw = json.dumps(obj,ensure_ascii=False)
    result = evaluate(GOOD,raw,GOOD['assessment'],POLICY,RUBRIC)
    assert all(c['pass'] for c in result['contracts'])
    assert all(e['candidate_quote'] in raw for e in GOOD['assessment']['evidence'].values())
    assert result['decision']['status'] == 'REVIEW'
    assert any('Stale assessment' in e for e in result['assessment_errors'])


@pytest.mark.parametrize('changed', ['customer','requirement','id','policy','rubric','candidate'])
def test_every_meaning_bearing_input_invalidates_stored_assessment(changed):
    case, policy, rubric = copy.deepcopy(GOOD), copy.deepcopy(POLICY), copy.deepcopy(RUBRIC)
    if changed in ('customer','requirement','id'): case[changed] += ' changed'
    elif changed == 'policy': policy['rules']['P5'] += ' New constraint.'
    elif changed == 'rubric': rubric['dimensions']['relevance']['2'] += ' New anchor.'
    else: case['candidate'] += ' '
    result = evaluate(case,case['candidate'],case['assessment'],policy,rubric)
    assert result['decision']['status'] == 'REVIEW'
    assert any('Stale assessment' in e for e in result['assessment_errors'])


@pytest.mark.parametrize('binding', [None, '', '0'*64, 123, 'z'*64])
def test_missing_malformed_or_wrong_binding_never_approves(binding):
    assessment=copy.deepcopy(GOOD['assessment'])
    if binding is None: assessment.pop('input_fingerprint')
    else: assessment['input_fingerprint']=binding
    assert evaluate(GOOD,GOOD['candidate'],assessment,POLICY,RUBRIC)['decision']['status']=='REVIEW'


def test_current_judge_cannot_override_a_stale_reference():
    case=copy.deepcopy(GOOD)
    case['customer'] += ' Please explain the process.'
    current=copy.deepcopy(case['assessment'])
    current['input_fingerprint']=assessment_input_fingerprint(case,case['candidate'],POLICY,RUBRIC)
    record=evaluate(case,case['candidate'],current,POLICY,RUBRIC,reference=case['assessment'])
    assert record['decision']['status']=='REVIEW'
    assert any(e.startswith('Reference: Stale') for e in record['assessment_errors'])


def test_known_contract_failure_still_blocks_with_stale_assessment():
    record=evaluate(GOOD,'plain text',GOOD['assessment'],POLICY,RUBRIC)
    assert record['decision']['status']=='BLOCK'
    assert any('Stale' in e for e in record['assessment_errors'])


def test_live_harness_binds_actual_inputs_not_fixture_candidate():
    case=copy.deepcopy(GOOD)
    obj=json.loads(case['candidate'])
    obj['reply']='Please provide your order number so support can start a return request for your unused lamp.'
    raw=json.dumps(obj)
    grade=copy.deepcopy(case['assessment'])
    grade.pop('input_fingerprint')
    for e in grade['evidence'].values(): e['candidate_quote']=obj['reply']
    def fake(model,instructions,payload,key):
        if model=='generator': return raw,{}
        assert payload['candidate']==raw
        assert payload['requirement']==case['requirement']
        assert 'input_fingerprint' not in payload
        return json.dumps(grade),{}
    record=run_live(case,POLICY,RUBRIC,'g','j','generator','judge','test',call=fake)
    assert record['decision']['status']=='ELIGIBLE'
    assert record['assessment']['input_fingerprint']==assessment_input_fingerprint(case,raw,POLICY,RUBRIC)
    assert record['assessment']['input_fingerprint']!=case['assessment']['input_fingerprint']


def test_judge_cannot_supply_its_own_binding():
    def fake(model,*args):
        return (GOOD['candidate'] if model=='generator' else json.dumps(GOOD['assessment'])),{}
    record=run_live(GOOD,POLICY,RUBRIC,'g','j','generator','judge','test',call=fake)
    assert record['decision']['status']=='REVIEW'
    assert any('assigned by the harness' in e for e in record['assessment_errors'])


def test_full_workshop_repair_preserves_baseline_and_requires_explicit_reassessment(tmp_path):
    baseline=(ROOT/'data/scenarios.json').read_bytes()
    path=tmp_path/'learner.json'
    initialize('matrix-02',path)
    exercise=load_exercise(path)
    assert exercise['case']['split']=='exercise'
    assert 'expected' not in exercise['case']
    before=tmp_path/'before'
    assert main(['demo','--exercise',str(path),'--out',str(before)])==0
    assert read_json(before/'report.json')['outcome']=='BLOCK'
    case=exercise['case']
    case['candidate']=json.dumps({'reply':case['candidate'],'action':'request_details','policy_ids':['P1']})
    path.write_text(json.dumps(exercise))
    stale=tmp_path/'stale'
    main(['demo','--exercise',str(path),'--out',str(stale)])
    assert read_json(stale/'report.json')['outcome']=='REVIEW'
    reassess(path,'Checked every dimension: only the JSON wrapper changed; the advice and quoted evidence remain supported.')
    after=tmp_path/'after'
    main(['demo','--exercise',str(path),'--out',str(after)])
    report=read_json(after/'report.json')
    assert report['outcome']=='ELIGIBLE'
    assert report['mode']=='exercise'
    assert report['provenance']['exercise']['review_history'][0]['note'].startswith('Checked every dimension')
    assert (ROOT/'data/scenarios.json').read_bytes()==baseline
    original=evaluate(CASES[1],CASES[1]['candidate'],CASES[1]['assessment'],POLICY,RUBRIC)
    assert original['decision']['status']=='BLOCK'


def test_reassessment_records_inputs_without_changing_scores_or_awarding_pass(tmp_path):
    path=tmp_path/'bad.json'
    initialize('matrix-01',path)
    old=load_exercise(path)
    reassess(path,'The reply remains irrelevant; retained all failing scores after review.')
    new=load_exercise(path)
    assert new['case']['assessment']['scores']==old['case']['assessment']['scores']
    assert evaluate(new['case'],new['case']['candidate'],new['case']['assessment'],POLICY,RUBRIC)['decision']['status']=='BLOCK'


def test_no_empty_note_or_invalid_quotes_can_be_rebound(tmp_path):
    path=tmp_path/'learner.json'
    initialize('matrix-04',path)
    with pytest.raises(ValueError): reassess(path,' ')
    value=load_exercise(path)
    value['case']['assessment']['evidence']['grounding']['candidate_quote']='fabricated excerpt'
    path.write_text(json.dumps(value)); before=path.read_bytes()
    with pytest.raises(ValueError): reassess(path,'Reviewed the evidence')
    assert path.read_bytes()==before


def test_exercise_writes_protect_baseline_existing_work_and_holdout(tmp_path):
    with pytest.raises(ValueError): initialize('matrix-02',ROOT/'data/scenarios.json')
    with pytest.raises(ValueError): reassess(ROOT/'data/scenarios.json','review')
    with pytest.raises(ValueError): initialize('holdout-13',tmp_path/'holdout.json')
    path=tmp_path/'learner.json';initialize('matrix-02',path);before=path.read_bytes()
    with pytest.raises(FileExistsError): initialize('matrix-01',path)
    assert path.read_bytes()==before


def test_missing_exercise_assessment_is_review_not_crash(tmp_path):
    path=tmp_path/'learner.json';initialize('matrix-04',path)
    value=load_exercise(path);value['case'].pop('assessment');path.write_text(json.dumps(value))
    main(['demo','--exercise',str(path),'--out',str(tmp_path/'report')])
    assert read_json(tmp_path/'report/report.json')['outcome']=='REVIEW'


@pytest.mark.parametrize('args', [['live','--exercise','x'],['demo','--exercise','x','--case','matrix-01'],
    ['demo','--exercise','x','--split','holdout']])
def test_exercise_options_cannot_mix_with_other_evaluation_modes(args):
    with pytest.raises(SystemExit) as exc: main(args)
    assert exc.value.code==2


def test_report_does_not_present_stale_maximum_scores_as_a_pass(tmp_path):
    path=tmp_path/'learner.json';initialize('matrix-04',path)
    value=load_exercise(path);value['case']['customer']+=' New context.';path.write_text(json.dumps(value))
    main(['demo','--exercise',str(path),'--out',str(tmp_path/'report')])
    report=read_json(tmp_path/'report/report.json');rendered=markdown(report)
    summary=teaching_summary(report['records'][0],RUBRIC)
    assert summary['purpose']=='NOT ESTABLISHED'
    assert summary['assessment_validity']=='INVALID / STALE'
    visible=rendered.split('<details>')[0]
    assert 'Scores are withheld' in visible
    assert 'Purpose judgment:' not in visible
    assert '| Score / required |' not in visible
    assert '<summary>Full technical evidence' in rendered


def test_report_prominently_shows_disagreement_and_both_reasons(tmp_path):
    main(['demo','--case','dev-09','--out',str(tmp_path)])
    report=read_json(tmp_path/'report.json');rendered=markdown(report)
    summary=teaching_summary(report['records'][0],RUBRIC)
    assert summary['purpose']=='DISPUTED'
    assert '**DISPUTED:**' in rendered
    assert 'Current judgment (disputed)' in rendered
    assert 'Authored reference (disputed)' in rendered
    assert 'guarantee' in rendered


def test_report_summary_explains_failure_and_required_change(tmp_path):
    main(['demo','--case','dev-12','--out',str(tmp_path)])
    report=read_json(tmp_path/'report.json');rendered=markdown(report)
    summary=teaching_summary(report['records'][0],RUBRIC)
    assert summary['contract']=='PASS' and summary['purpose']=='FAIL'
    assert 'What must happen next' in rendered
    assert 'Your refund is already processed' in rendered
    assert 'fabricated' in rendered or 'invented' in rendered
