"""Acceptance tests assert outcomes and failure boundaries, not snapshot cosmetics."""
import copy
import json
import subprocess
import sys
import urllib.error

import pytest

from rules_purpose.core import (ROOT, aggregate, assessment_errors, contracts, decide,
                                evaluate, fingerprint, read_json, strict_json)
from rules_purpose.__main__ import main, run_live
from rules_purpose.provider import ProviderError, respond
from rules_purpose.report import markdown

POLICY = read_json(ROOT/'data/policy.json')
RUBRIC = read_json(ROOT/'data/rubric.json')
DATASET = read_json(ROOT/'data/scenarios.json')
CASES = DATASET['cases']
GOOD = CASES[3]


def offline(case):
    simulated = case.get('simulated_judge')
    return evaluate(case,case['candidate'],simulated or case['assessment'],POLICY,RUBRIC,
                    reference=case['assessment'] if simulated else None)


@pytest.mark.parametrize('case', CASES, ids=lambda c:c['id'])
def test_authored_case_has_valid_evidence_and_expected_decision(case):
    result = offline(case)
    assert not result['assessment_errors']
    assert result['decision']['status'] == case['expected']


def test_four_quadrants_demonstrate_independent_layers():
    results = [offline(c) for c in CASES[:4]]
    assert [all(x['pass'] for x in r['contracts']) for r in results] == [True,False,False,True]
    assert [all(s == 2 for s in r['assessment']['scores'].values()) for r in results] == [False,True,False,True]


@pytest.mark.parametrize('raw', ['{}','[]','null','42','true','not json',
    '{"reply":"x","reply":"y","action":"escalate","policy_ids":["P1"]}',
    '{"reply":NaN,"action":"escalate","policy_ids":["P1"]}'])
def test_invalid_contracts_block_even_without_a_judge(raw):
    result = evaluate(GOOD,raw,None,POLICY,RUBRIC)
    assert result['decision']['status'] == 'BLOCK'


@pytest.mark.parametrize('field,value', [('reply',' '),('reply','x'*1201),('reply',7),
    ('action','refund'),('action',[]),('policy_ids',[]),('policy_ids',['P404']),
    ('policy_ids',['P1','P1']),('policy_ids',[{}]),('extra','unknown')])
def test_contract_boundary_and_wrong_types(field,value):
    obj = json.loads(GOOD['candidate'])
    obj[field] = value
    assert not all(c['pass'] for c in contracts(json.dumps(obj), POLICY))


def test_valid_policy_id_is_not_semantic_support():
    result = offline(CASES[11])
    assert all(c['pass'] for c in result['contracts'])
    assert result['assessment']['scores']['grounding'] == 0
    assert result['decision']['status'] == 'BLOCK'


@pytest.mark.parametrize('mutation', ['missing','bool','float','too_high','bad_quote','bad_policy','empty_reason','extra'])
def test_untrustworthy_grading_evidence_cannot_make_candidate_eligible(mutation):
    a = copy.deepcopy(GOOD['assessment'])
    if mutation == 'missing': del a['scores']['grounding']
    if mutation == 'bool': a['scores']['grounding'] = True
    if mutation == 'float': a['scores']['grounding'] = 2.0
    if mutation == 'too_high': a['scores']['grounding'] = 3
    if mutation == 'bad_quote': a['evidence']['grounding']['candidate_quote'] = 'invented quote'
    if mutation == 'bad_policy': a['evidence']['grounding']['policy_id'] = 'P404'
    if mutation == 'empty_reason': a['evidence']['grounding']['reason'] = ''
    if mutation == 'extra': a['release_decision'] = 'ELIGIBLE'
    result = evaluate(GOOD,GOOD['candidate'],a,POLICY,RUBRIC)
    assert result['decision']['status'] == 'REVIEW'


def test_missing_evidence_and_empty_run_require_review():
    assert evaluate(GOOD,GOOD['candidate'],None,POLICY,RUBRIC)['decision']['status'] == 'REVIEW'
    assert aggregate([]) == 'REVIEW'
    assert decide([], GOOD['assessment'], [], RUBRIC)['status'] == 'REVIEW'


def test_no_average_can_hide_a_critical_failure():
    a = copy.deepcopy(GOOD['assessment'])
    a['scores']['grounding'] = 0
    assert evaluate(GOOD,GOOD['candidate'],a,POLICY,RUBRIC)['decision']['status'] == 'BLOCK'


def test_material_disagreement_requires_review():
    record = offline(CASES[8])
    assert record['disagreement']
    assert record['decision']['status'] == 'REVIEW'


def test_grader_is_not_an_oracle_even_with_real_quotes():
    # Intentionally false conclusions can have valid quotes. Semantic review is essential.
    c = CASES[8]
    assert assessment_errors(c['simulated_judge'],c['candidate'],POLICY) == []
    assert c['simulated_judge']['scores'] != c['assessment']['scores']


def test_split_ids_unique_and_heldout_not_in_default_demo(tmp_path):
    assert len({c['id'] for c in CASES}) == 16
    assert sum(c['split']=='holdout' for c in CASES) == 4
    assert main(['demo','--out',str(tmp_path)]) == 0
    report = read_json(tmp_path/'report.json')
    assert len(report['records']) == 12
    assert all(r['split']=='dev' for r in report['records'])


def test_demo_uses_no_provider_and_has_explicit_fixture_provenance(tmp_path,monkeypatch):
    def forbidden(*args,**kwargs): raise AssertionError('Offline must not call network')
    monkeypatch.setattr('urllib.request.urlopen',forbidden)
    assert main(['demo','--split','all','--out',str(tmp_path)]) == 0
    report = read_json(tmp_path/'report.json')
    assert report['outcome'] == 'BLOCK'
    assert 'No live API calls' in report['interpretation']
    assert 'not independent human' in report['provenance']['dataset_provenance']
    assert (tmp_path/'report.md').is_file()


@pytest.mark.parametrize('args', [['demo','--repeat','2'],['demo','--case','missing'],
    ['demo','--case','holdout-13'],['demo','--repeat','0'],['demo','--repeat','6'],['live']])
def test_bad_cli_selection_or_configuration_fails(args):
    with pytest.raises(SystemExit) as error: main(args)
    assert error.value.code == 2


def test_live_requires_key_without_network(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    with pytest.raises(SystemExit): main(['live','--model','test','--judge-model','test'])


def fake_metadata(model):
    return {'requested_model':model,'returned_model':'test-snapshot','response_id':'test-response','usage':{}}


def test_live_separates_generation_from_grading_and_excludes_reference_labels():
    calls=[]
    def fake(model,instructions,payload,key):
        calls.append((model,payload))
        assert key == 'test-only'
        assert 'assessment' not in payload and 'expected' not in payload
        return (GOOD['candidate'] if len(calls)==1 else json.dumps({k:v for k,v in GOOD['assessment'].items() if k != 'input_fingerprint'}), fake_metadata(model))
    result = run_live(GOOD,POLICY,RUBRIC,'generate','judge','generator','grader','test-only',call=fake)
    assert [c[0] for c in calls] == ['generator','grader']
    assert 'candidate' not in calls[0][1]
    assert calls[1][1]['candidate'] == GOOD['candidate']
    assert result['decision']['status'] == 'ELIGIBLE'
    assert result['assessment_source'] == 'live_model'


def test_calibration_uses_fixed_candidate_and_identifies_disagreement():
    case=CASES[8]
    def fake(model,instructions,payload,key):
        assert model == 'grader'
        assert payload['candidate'] == case['candidate']
        return json.dumps({k:v for k,v in case['simulated_judge'].items() if k != 'input_fingerprint'}),fake_metadata(model)
    result = run_live(case,POLICY,RUBRIC,'g','j',None,'grader','test',calibrate=True,call=fake)
    assert result['decision']['status'] == 'REVIEW'
    assert result['disagreement']


@pytest.mark.parametrize('phase', ['generation','judge','judge_json'])
def test_live_provider_failures_are_reportable_review(phase):
    count=0
    def fake(model,instructions,payload,key):
        nonlocal count
        count+=1
        if phase == 'generation' or (phase == 'judge' and count == 2):
            raise ProviderError('Synthetic unavailable provider')
        return (GOOD['candidate'] if count == 1 else 'not JSON'),fake_metadata(model)
    result=run_live(GOOD,POLICY,RUBRIC,'g','j','generator','grader','test',call=fake)
    assert result['decision']['status']=='REVIEW'
    assert result['assessment_errors']


def test_known_contract_failure_blocks_despite_judge_outage():
    def fake(model,instructions,payload,key):
        if model == 'generator': return 'broken JSON',fake_metadata(model)
        raise ProviderError('Synthetic outage')
    assert run_live(GOOD,POLICY,RUBRIC,'g','j','generator','grader','test',call=fake)['decision']['status']=='BLOCK'


def test_aggregate_does_not_hide_unstable_trials():
    record=lambda status:{'decision':{'status':status}}
    assert aggregate([record('ELIGIBLE'),record('BLOCK')])=='BLOCK'
    assert aggregate([record('ELIGIBLE'),record('REVIEW')])=='REVIEW'
    assert aggregate([record('ELIGIBLE')])=='ELIGIBLE'


def test_provider_request_and_output_parsing(monkeypatch):
    class Response:
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def read(self): return json.dumps({'status':'completed','model':'snapshot','id':'id',
            'output':[{'type':'reasoning'},{'type':'message','content':[{'type':'output_text','text':'hello'}]}]}).encode()
    def fake(request,timeout):
        body=json.loads(request.data)
        assert request.full_url == 'https://api.openai.com/v1/responses'
        assert body['store'] is False and timeout == 60
        assert body['model']=='chosen-model' and body['instructions']=='instructions'
        assert request.get_header('Authorization')=='Bearer secret-test-value'
        return Response()
    monkeypatch.setattr('urllib.request.urlopen',fake)
    text,metadata=respond('chosen-model','instructions',{'customer':'test'},'secret-test-value')
    assert text=='hello' and metadata['returned_model']=='snapshot'
    assert 'secret-test-value' not in json.dumps(metadata)


@pytest.mark.parametrize('body', [{'status':'incomplete'}, {'status':'completed','output':[]},
    {'status':'completed','output':42}, {'status':'completed','output':[{'type':'message','content':[{'type':'refusal','refusal':'no'}]}]}])
def test_incomplete_or_unusable_provider_output_is_not_success(monkeypatch,body):
    class Response:
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def read(self): return json.dumps(body).encode()
    monkeypatch.setattr('urllib.request.urlopen',lambda *a,**k:Response())
    with pytest.raises(ProviderError): respond('test','test',{},'test')


def test_provider_error_does_not_leak_error_details(monkeypatch):
    def fake(*args,**kwargs):
        raise urllib.error.HTTPError('url',401,'secret-test-value',{},None)
    monkeypatch.setattr('urllib.request.urlopen',fake)
    with pytest.raises(ProviderError,match='Provider HTTP 401') as e: respond('test','test',{},'test')
    assert 'secret-test-value' not in str(e.value)


def test_report_escapes_untrusted_html(tmp_path):
    main(['demo','--case','matrix-04','--out',str(tmp_path)])
    report=read_json(tmp_path/'report.json')
    report['records'][0]['candidate']='</pre><script>alert(1)</script>'
    rendered=markdown(report)
    assert '<script>' not in rendered and '&lt;script&gt;' in rendered


def test_fingerprint_changes_when_policy_changes():
    changed=copy.deepcopy(POLICY)
    changed['rules']['P1']='Different rule'
    assert fingerprint(changed)!=fingerprint(POLICY)
