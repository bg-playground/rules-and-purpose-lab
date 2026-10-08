"""Teaching-first Markdown, with complete machine-readable evidence retained."""
import html
import json
from collections import Counter
from pathlib import Path

from .core import DIMENSIONS, purpose_pass


def safe(value):
    return html.escape(str(value)).replace('|', '&#124;').replace('\n', '<br>')


def block(value):
    return '<pre>' + html.escape(str(value)) + '</pre>'


def details(title, value):
    return ['<details>', '<summary>' + safe(title) + '</summary>', '',
            block(json.dumps(value, indent=2, ensure_ascii=False)), '', '</details>']


def teaching_summary(record, rubric):
    checks = record['contracts']
    contract = 'UNAVAILABLE' if not checks else 'PASS' if all(c['pass'] for c in checks) else 'FAIL'
    assessment = record.get('assessment')
    errors = record.get('assessment_errors', [])
    if assessment is None:
        validity, purpose = 'UNAVAILABLE', 'NOT ESTABLISHED'
    elif errors:
        validity, purpose = 'INVALID / STALE', 'NOT ESTABLISHED'
    elif record.get('disagreement'):
        validity, purpose = 'VALID INPUTS; DISPUTED JUDGMENT', 'DISPUTED'
    else:
        validity = 'VALID INPUTS AND EXCERPTS'
        purpose = 'PASS' if purpose_pass(assessment, rubric) else 'FAIL'
    if record['decision']['status'] == 'ELIGIBLE':
        next_step = "No change required by this scenario's criteria; this is not production release approval."
    elif contract == 'FAIL':
        next_step = 'Repair the output contract, then reassess the changed candidate; the earlier assessment will be stale.'
    elif errors or assessment is None:
        next_step = 'Obtain or redo the assessment for the exact current inputs. Do not reuse stale or invalid scores.'
    elif record.get('disagreement'):
        next_step = 'Review the conflicting reasons against policy and document which judgment is defensible; do not average the scores.'
    else:
        next_step = 'Revise the response and reassess it against this requirement: ' + record['requirement']
    return {'contract':contract, 'purpose':purpose, 'assessment_validity':validity, 'next_step':next_step}


def markdown(report):
    counts = Counter(r['decision']['status'] for r in report['records'])
    lines = ['# Rules & Purpose Lab — evidence report', '',
             f"**Mode:** {safe(report['mode'])} · **Run outcome:** {safe(report['outcome'])}", '',
             report['interpretation'], '',
             f"Counts: {counts['BLOCK']} Block / {counts['REVIEW']} Review / {counts['ELIGIBLE']} Eligible", '',
             'Purpose scores are judgments, not approval. Invalid or stale evidence establishes no purpose result; disagreements remain disputed.', '',
             '| Scenario / trial | Contract | Purpose | Assessment validity | Decision |',
             '| --- | --- | --- | --- | --- |']
    for record in report['records']:
        summary = teaching_summary(record, report['rubric'])
        row = [f"{record['scenario_id']} / {record.get('trial', 1)}", summary['contract'],
               summary['purpose'],summary['assessment_validity'],record['decision']['status']]
        lines.append('| ' + ' | '.join(safe(v) for v in row) + ' |')
    for record in report['records']:
        summary = teaching_summary(record, report['rubric'])
        lines += ['', f"## {safe(record['scenario_id'])} — trial {record.get('trial', 1)}", '',
                  '**Customer:** ' + safe(record['customer']), '',
                  '| Decision element | Explanation |', '| --- | --- |',
                  '| Intended purpose / requirement | ' + safe(record['requirement']) + ' |',
                  '| Contract result | ' + summary['contract'] + ' |',
                  '| Purpose result | ' + summary['purpose'] + ' |',
                  '| Assessment validity | ' + summary['assessment_validity'] + ' |',
                  '| Assessment source | ' + safe(record['assessment_source']) + ' |',
                  '| Release decision | ' + safe(record['decision']['status'] + ' — ' + record['decision']['reason']) + ' |',
                  '| What must happen next | ' + safe(summary['next_step']) + ' |', '',
                  '**Observed candidate:**', '', block(record.get('candidate') or '(unavailable)'), '',
                  '**Decisive checks and evidence:**', '']
        failures = [c for c in record['contracts'] if not c['pass']]
        for check in failures:
            lines.append('- Contract ' + safe(check['id']) + ': ' + safe(check['detail']))
        if record.get('assessment_errors'):
            lines += ['- ' + safe(e) for e in record['assessment_errors']]
            lines += ['', 'Scores are withheld here because the required evidence is invalid or unavailable. Raw values remain in the technical details.']
        elif record.get('assessment') is not None:
            if record.get('disagreement'):
                lines += ['**DISPUTED:** current and reference assessments cross a pass/fail threshold. Neither is presented as an approved result.', '']
                assessments = [('Current judgment (disputed)', record['assessment']),
                               ('Authored reference (disputed)', record['reference'])]
            else:
                assessments = [('Purpose judgment', record['assessment'])]
            for label, assessment in assessments:
                lines += ['', '**' + label + ':**', '',
                          '| Dimension | Score / required | Candidate excerpt | Policy excerpt | Reason |',
                          '| --- | --- | --- | --- | --- |']
                for dimension in DIMENSIONS:
                    evidence = assessment['evidence'][dimension]
                    row = [dimension.capitalize(),f"{assessment['scores'][dimension]} / {report['rubric']['thresholds'][dimension]}",
                           evidence['candidate_quote'], evidence['policy_id'] + ': ' + evidence['policy_quote'], evidence['reason']]
                    lines.append('| ' + ' | '.join(safe(v) for v in row) + ' |')
        else:
            lines.append('No usable assessment is available. Purpose is not established.')
        lines += [''] + details('Full technical evidence for this scenario', record)
    lines += ['', '## Run provenance and evaluation criteria', '']
    lines += details('Prompts, versions, fingerprints, and exercise review notes', report['provenance'])
    lines += [''] + details('Policy and rubric snapshots used in this run', {'policy':report['policy'],'rubric':report['rubric']})
    return '\n'.join(lines) + '\n'


def write_report(report, directory):
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    (path / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    (path / 'report.md').write_text(markdown(report), encoding='utf-8')
