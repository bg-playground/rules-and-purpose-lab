"""Build the credential-free learning site using Python's standard library."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import re, shutil
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'
REPO = 'https://github.com/bg-playground/rules-and-purpose-lab'
BASE = 'https://bg-playground.github.io/rules-and-purpose-lab/'

def inline(text):
    text = escape(text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    def link(m):
        label, href = m.groups()
        if href == '../workshop.md': href = 'workshop.html'
        elif href.startswith(('http:', 'https:')): pass
        else: href = REPO + '/blob/main/docs/' + href
        return f'<a href="{href}">{label}</a>'
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, text)

def markdown(text):
    # Deliberately supports the headings, lists, links, and fences in workshop.md.
    result, para, listing, fence = [], [], None, None
    def flush():
        if para:
            result.append('<p>' + inline(' '.join(para)) + '</p>'); para.clear()
    for line in text.splitlines():
        if fence is not None:
            if line.startswith('```'):
                result.append('<pre><code>'+escape('\n'.join(fence))+'</code></pre>'); fence=None
            else: fence.append(line)
            continue
        if line.startswith('```'):
            flush()
            if listing: result.append('</'+listing+'>'); listing=None
            fence=[]; continue
        item=re.match(r'^(?:([-*]) |(\d+)\. )(.*)',line)
        if listing and not item: result.append('</'+listing+'>'); listing=None
        if not line.strip(): flush(); continue
        heading=re.match(r'^(#{1,6}) (.*)',line)
        if heading:
            flush(); n=len(heading[1]); result.append(f'<h{n}>{inline(heading[2])}</h{n}>')
        elif item:
            flush(); tag='ul' if item[1] else 'ol'
            if listing != tag:
                if listing: result.append('</'+listing+'>')
                result.append('<'+tag+'>'); listing=tag
            result.append('<li>'+inline(item[3])+'</li>')
        else: para.append(line)
    flush()
    if listing: result.append('</'+listing+'>')
    if fence is not None: raise ValueError('Unclosed Markdown fence')
    return '\n'.join(result)

def page(title, body, active, desc):
    nav=''.join(f'<a href="{href}"'+(' aria-current="page"' if key==active else '')+f'>{label}</a>' for key,href,label in [('home','index.html','Introduction'),('slides','slides.html','Slides'),('workshop','workshop.html','Workshop')])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} | Rules &amp; Purpose Lab</title><meta name="description" content="{escape(desc)}"><link rel="canonical" href="{BASE}{'index.html' if active=='home' else active+'.html'}"><link rel="stylesheet" href="styles.css"></head><body><a class="skip" href="#main">Skip to content</a><header><div class="header-inner"><a class="brand" href="index.html">Rules &amp; Purpose <span>Lab</span></a><nav aria-label="Main navigation">{nav}<a href="{REPO}">Repository</a></nav></div></header><main id="main">{body}</main><footer><p>A teaching project by <a href="https://bradguider.com/work/#teaching">Brad Guider</a>.</p><p>Fictional examples. Authored assessments. Teaching effectiveness awaits a participant trial.</p><a href="{REPO}/blob/main/docs/limitations.md">Evidence and limitations</a></footer></body></html>'''

def table(headers, rows):
    return '<div class="table-wrap"><table><thead><tr>'+''.join('<th scope="col">'+h+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+c+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></div>'

matrix=table(['Candidate response','Contract','Purpose','Decision'],[
['Valid JSON with irrelevant catalog advice','Pass','Fail','<strong>Block</strong>'],['Helpful return advice in plain text','Fail','Pass','<strong>Block</strong>'],['Plain text claiming a completed refund','Fail','Fail','<strong>Block</strong>'],['Valid JSON with supported return advice','Pass','Pass','<strong>Eligible</strong>']])
downloads='<div class="actions"><a class="button" href="downloads/Rules_and_Purpose_Lab_Teaching_Deck.pdf">Open PDF</a><a href="downloads/Rules_and_Purpose_Lab_Teaching_Deck.pptx" download>Download PowerPoint</a></div>'
intro=f'''<section class="intro"><div><p class="eyebrow">A practical teaching lab</p><h1>Rules &amp;<br>Purpose Lab</h1><p class="lead">Did the system obey the rule?<br>Did the result fulfill its purpose?</p><p>Explore how deterministic testing and AI evaluation contribute different evidence to a release decision.</p><div class="actions"><a class="button" href="slides.html">View the slides</a><a href="workshop.html">Try the 20-minute workshop</a></div><p class="small">Python 3.11+. No API key needed for the workshop.</p></div><img src="assets/cover-art.webp" width="1400" height="788" alt="" /></section>
<section class="reading"><p class="eyebrow">One customer request</p><h2>Four responses. Different evidence.</h2><blockquote>“My unused desk lamp arrived 10 days ago. I would like to return it. What should I do?”</blockquote><p>The policy allows an unused-product return request within 30 days. Support needs the order number. The assistant can draft advice, but cannot process a refund.</p>{matrix}<p class="small">AI-assisted authored teaching examples, not measured model performance. Eligible applies to the evaluated scenario and criteria, not production deployment.</p></section>
<section class="reading"><h2>Run the example</h2><pre><code>git clone https://github.com/bg-playground/rules-and-purpose-lab.git\ncd rules-and-purpose-lab\npython -m rules_purpose demo</code></pre><p>Open <code>reports/latest/report.md</code>. The report connects each requirement, response, check, and assessment to its decision. The demo deliberately includes bad responses, so a successful run can report <strong>Block</strong>.</p><p>On Windows, use <code>py</code> instead of <code>python</code> if that is how Python is installed.</p><a href="{REPO}/blob/main/examples/report.md">Inspect an example report</a></section>'''
slides=[]
def slide(n,title,content):
    slides.append(f'<section class="slide" id="slide-{n}" aria-labelledby="title-{n}"><p class="eyebrow">{n:02d} / 07</p><h2 id="title-{n}">{title}</h2>{content}</section>')
slide(1,'Rules &amp; Purpose Lab','<p class="lead">Deterministic testing tells us whether the system obeyed a rule. AI evaluation helps us determine whether the result fulfilled its purpose.</p><p>A trustworthy release process needs both. This short introduction leads into a hands-on customer-support workshop.</p><p class="small">Brad Guider · Fictional authored examples</p>')
slide(2,'Contracts and purpose',table(['Deterministic contracts','Purpose evaluation'],[['Did the response obey the explicit rules?','Did the response address the customer’s need?'],['Valid JSON, required fields, allowed action, existing policy IDs','Relevant advice, supported claims, a feasible next step']])+'<p>Deterministic checks are one kind of evaluation. Code, models, and people can contribute evidence about purpose.</p>')
slide(3,'One customer, four outcomes','<blockquote>“My unused lamp arrived 10 days ago. How do I return it?”</blockquote>'+matrix+'<p class="small">Authored teaching fixtures. Eligible applies only to this scenario and its criteria.</p>')
slide(4,'Evidence can become stale','<div class="comparison"><div><h3>An original answer</h3><blockquote>“Please provide your order number so support can help start a return request.”</blockquote></div><div><h3>An added claim</h3><blockquote>“Your refund has already been processed.”</blockquote></div></div><p>Old quotations still match, but the evaluated input has changed. The assessment is stale, so the result needs <strong>Review</strong>.</p><p class="small">This detects stale evidence. It does not establish a fresh semantic assessment of the added claim. A defensible reassessment may block the response.</p>')
slide(5,'The release decision',table(['Decision','Evidence required'],[['<strong>Block</strong>','A known contract failure, or a valid uncontested purpose failure'],['<strong>Review</strong>','Missing or stale evidence, invalid grading, or a material disagreement'],['<strong>Eligible</strong>','All required evidence is valid and every criterion is satisfied']])+'<p>A high average cannot cancel a failing requirement. A known contract failure still blocks when grading is unavailable.</p>')
slide(6,'The hands-on workshop','<ol class="agenda"><li><strong>Predict</strong><span>Which responses should be eligible?</span></li><li><strong>Inspect</strong><span>Trace a decision to its checks and excerpts.</span></li><li><strong>Repair and reassess</strong><span>Change an exercise copy while preserving the baseline.</span></li><li><strong>Challenge the judge</strong><span>Explain why confident grading may be wrong.</span></li></ol><p><a href="workshop.html">Open the workshop</a></p>')
slide(7,'The teaching trial','<p class="lead">The next evidence comes from learners.</p><p>Can they complete the exercise and explain why a passing contract can still lead to a blocked release?</p><p>Automated acceptance checks concern lab behavior. Teaching effectiveness remains to be observed. No provider-backed model-quality experiment has been claimed.</p><pre><code>python -m rules_purpose demo</code></pre><a href="workshop.html">Continue to the workshop</a>')
slides_body='<div class="page-heading"><p class="eyebrow">Teaching deck · Seven slides</p><h1>Rules, purpose, and release evidence</h1><p>Read at your own pace, or download the deck for a short facilitated introduction.</p>'+downloads+'<nav class="slide-index" aria-label="Slide navigation">'+''.join(f'<a href="#slide-{i}">Slide {i}</a>' for i in range(1,8))+'</nav></div><div class="slide-list">'+''.join(slides)+'</div><p class="reading small">Adapted from the <a href="'+REPO+'/blob/main/docs/presentation/README.md">editable deck and facilitator notes</a>. Browser text reflows for smaller screens. The PDF preserves the original slide design.</p>'
workshop=markdown((ROOT/'docs/workshop.md').read_text())
workshop=workshop.replace('<h1>A 20-minute workshop: rules, purpose, and release evidence</h1>','<p class="eyebrow">Hands-on learning</p><h1>The 20-minute workshop</h1><p><a href="slides.html">Read the slides first</a> or follow the steps below with a local checkout.</p>')
# Link the README reference to the introduction without altering instructions.
workshop=workshop.replace('Read the four candidates in the README.','Read the <a href="index.html">four candidates in the introduction</a>.')
if OUT.exists(): shutil.rmtree(OUT)
shutil.copytree(ROOT/'site',OUT)
(OUT/'downloads').mkdir(exist_ok=True)
for ext in ['pdf','pptx']:
    shutil.copyfile(ROOT/f'docs/presentation/Rules_and_Purpose_Lab_Teaching_Deck.{ext}',OUT/f'downloads/Rules_and_Purpose_Lab_Teaching_Deck.{ext}')
for name,title,body,active,desc in [('index.html','Introduction',intro,'home','A practical teaching lab about contract compliance, purpose evaluation, and release evidence.'),('slides.html','Teaching slides',slides_body,'slides','Seven browser-readable slides with PDF and PowerPoint downloads.'),('workshop.html','Workshop','<article class="workshop reading">'+workshop+'</article>','workshop','A 20-minute credential-free exercise in evidence-grounded release decisions.')]:
    (OUT/name).write_text(page(title,body,active,desc))
(OUT/'.nojekyll').touch()
class Links(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]; self.ids=[]; self.h1=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='h1':self.h1+=1
        for attr in ['href','src']:
            if attr in a:self.links.append(a[attr])
parsers={p.name:Links() for p in OUT.glob('*.html')}
for name,parser in parsers.items():
    parser.feed((OUT/name).read_text()); assert parser.h1==1; assert len(parser.ids)==len(set(parser.ids))
for name,parser in parsers.items():
    for href in parser.links:
        u=urlsplit(href)
        if u.scheme:continue
        target=unquote(u.path) or name
        assert (OUT/target).is_file(),(name,href)
        if u.fragment:assert u.fragment in parsers[target].ids,(name,href)
assert len(re.findall(r'class="slide"', (OUT/'slides.html').read_text()))==7
print('Built and verified 3 pages, 7 slides, local links, fragments, and download files.')
