"""Human-readable reports keep the detailed evidence alongside the decision."""
import html
import json
from collections import Counter
from pathlib import Path


def safe(value):
    return html.escape(str(value)).replace('|', '&#124;').replace('\n', '<br>')


def block(value):
    # Escaped pre blocks prevent candidate text from becoming Markdown/HTML.
    return '<pre>' + html.escape(str(value)) + '</pre>'


def markdown(report):
    counts = Counter(r['decision']['status'] for r in report['records'])
    lines = ['# Rules & Purpose Lab — evidence report', '',
             f"**Mode:** {safe(report['mode'])} · **Run outcome:** {safe(report['outcome'])}", '',
             report['interpretation'], '',
             f"Counts: {counts['BLOCK']} Block / {counts['REVIEW']} Review / {counts['ELIGIBLE']} Eligible", '',
             '| Scenario | Contract | Purpose scores (R/G/A) | Decision |',
             '| --- | --- | --- | --- |']
    for r in report['records']:
        c = 'PASS' if r['contracts'] and all(x['pass'] for x in r['contracts']) else 'FAIL' if r['contracts'] else 'UNAVAILABLE'
        a = r.get('assessment')
        scores = '/'.join(str(a['scores'][d]) for d in ('relevance', 'grounding', 'actionability')) if isinstance(a, dict) and isinstance(a.get('scores'), dict) and all(d in a['scores'] for d in ('relevance','grounding','actionability')) else 'unavailable'
        lines.append(f"| {safe(r['scenario_id'])} / {r.get('trial', 1)} | {c} | {safe(scores)} | {r['decision']['status']} |")
    lines += ['', '## Provenance', '', block(json.dumps(report['provenance'], indent=2, ensure_ascii=False))]
    for r in report['records']:
        lines += ['', f"## {safe(r['scenario_id'])} — trial {r.get('trial', 1)}", '',
                  '**Requirement:** ' + safe(r['requirement']), '',
                  '**Customer:** ' + safe(r['customer']), '',
                  '**Observed candidate:**', '', block(r.get('candidate') or '(unavailable)'), '',
                  '**Decision:** ' + safe(r['decision']['status'] + ' — ' + r['decision']['reason']), '',
                  '**Checks and evaluation evidence:**', '',
                  block(json.dumps({k:v for k,v in r.items() if k not in ('customer','candidate','requirement')}, indent=2, ensure_ascii=False))]
    lines += ['', '## Policy and rubric used', '', block(json.dumps({'policy':report['policy'],'rubric':report['rubric']},indent=2,ensure_ascii=False)), '']
    return '\n'.join(lines)


def write_report(report, directory):
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    (path / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    (path / 'report.md').write_text(markdown(report), encoding='utf-8')
