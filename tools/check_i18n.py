#!/usr/bin/env python3
"""Prüft die Quellen der Seite und, wenn ein Ausgabeordner angegeben ist, die von Hugo gebaute Seite.

Aufruf im Repo-Wurzelverzeichnis:
  python3 tools/check_i18n.py            # nur Quellen (data/, layouts/, downloads/, PDF-Quelle)
  python3 tools/check_i18n.py public     # zusätzlich die gebaute Seite im Ordner public/

Quellen: Deutsch und Englisch vollständig und gleich aufgebaut, gültige Befunde, Downloads passen zur Quelle.
Gebaute Seite: gleiche IDs, Anker und Tag-Anzahlen in beiden Sprachen, kein deutscher Rest im Englischen,
alle internen Links und Anker haben ein Ziel, Feeds und Sitemap passen zu status.json, keine Vorlagenreste,
keine typischen privaten Angaben (interne IP-Adressen, interne Hostnamen, Work-Item-Nummern).

Nicht geprüft: Qualität der Übersetzung, externe Links, Barrierefreiheit, inhaltliche Richtigkeit.
Der Scan auf private Angaben ist ein Netz für Versehen und ersetzt die Durchsicht vor dem Merge nicht.
Exit 0 = in Ordnung, Exit 1 = Abweichung (wird ausgegeben)."""
import glob, json, os, re, subprocess, sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

UML = re.compile(r'[äöüÄÖÜß]')
errors = []

class Scan(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.tags={}; self.nav=[]; self.refs=[]; self.skip=False; self.text=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs); self.tags[tag]=self.tags.get(tag,0)+1
        if a.get('id'): self.ids.append(a['id'])
        if tag=='a' and (a.get('href') or '').startswith('#'): self.nav.append(a['href'])
        for k in ('href','src'):
            if a.get(k) and tag in ('a','img','link','script','source'): self.refs.append((tag, a.get('rel',''), a[k]))
        if tag in('script','style'): self.skip=True
    def handle_endtag(self, tag):
        if tag in('script','style'): self.skip=False
    def handle_data(self, d):
        if not self.skip: self.text.append(d)

def scan_text(s):
    p=Scan(); p.feed(s); return p

def load(path):
    return json.load(open(path,encoding='utf-8'))

def shape(o):
    """Aufbau ohne Inhalte: gleiche Schlüssel und Listenlängen in beiden Sprachen."""
    if isinstance(o,dict): return {k:shape(v) for k,v in sorted(o.items())}
    if isinstance(o,list): return [shape(v) for v in o]
    return type(o).__name__ if not isinstance(o,str) else 'str'

# ---------- Quellen ----------

# status.json: beide Sprachen vollständig
d=load('data/status.json'); e=d.get('en')
if not e: errors.append('status.json: Objekt "en" fehlt')
else:
    if not d.get('last_test') or not e.get('last_test'): errors.append('status.json: last_test (de) oder en.last_test fehlt')
    if d.get('as_of') is None or len(d.get('history',[]))!=len(e.get('history',[])): errors.append('status.json: as_of oder history fehlt/ungleich')
    for k in ('title','evidence'):
        if not e.get(k): errors.append(f'status.json en.{k} fehlt')
    for k in ('confirmed','not_yet_verified','known_issues','history'):
        if len(e.get(k,[]))!=len(d.get(k,[])): errors.append(f'status.json {k}: de={len(d.get(k,[]))} en={len(e.get(k,[]))}')
    ids={m['id'] for m in d['milestones']}
    if ids!=set(e.get('milestones',{})): errors.append(f'status.json en.milestones passt nicht zu den IDs {sorted(ids)}')
    if UML.search(json.dumps(e,ensure_ascii=False)): errors.append('status.json: Umlaute im englischen Teil')
    if d.get('visibility')!='public' or d.get('approved') is not True: errors.append('status.json: visibility/approved nicht auf öffentlich freigegeben')
    dates=[h['date'] for h in d.get('history',[])]
    if dates!=sorted(dates): errors.append('status.json: history nicht in zeitlicher Reihenfolge (neue Einträge hinten anfügen)')

# Befunde: beide Sprachen, gültige Typen und Zustände, neueste zuerst
try:
    fe=load('data/findings.json')['entries']
    ids=[x['id'] for x in fe]
    if len(set(ids))!=len(ids): errors.append('findings.json: doppelte IDs')
    if [x['date'] for x in fe]!=sorted([x['date'] for x in fe],reverse=True): errors.append('findings.json: nicht neueste zuerst')
    for x in fe:
        if x['type'] not in ('finding','problem','correction'): errors.append(f"findings.json {x['id']}: Typ ungültig")
        if x.get('state') not in (None,'open','resolved'): errors.append(f"findings.json {x['id']}: Zustand ungültig")
        if x['type']=='problem' and not x.get('state'): errors.append(f"findings.json {x['id']}: Problem ohne Zustand")
        for l in ('de','en'):
            if not x.get(l,{}).get('title') or not x.get(l,{}).get('text'): errors.append(f"findings.json {x['id']}: {l} unvollständig")
        if UML.search(x.get('en',{}).get('title','')+x.get('en',{}).get('text','')): errors.append(f"findings.json {x['id']}: Umlaute im Englischen")
except FileNotFoundError:
    errors.append('data/findings.json fehlt')

# Nachbauen, Umbau, Persona: Deutsch und Englisch gleich aufgebaut
for name in ('steps','umbau'):
    try:
        c=load(f'data/{name}.json')
        if shape(c.get('de'))!=shape(c.get('en')): errors.append(f'{name}.json: Aufbau von de und en unterschiedlich')
    except FileNotFoundError:
        errors.append(f'data/{name}.json fehlt')
try:
    c=load('data/soul.json')
    if shape(c['page'].get('de'))!=shape(c['page'].get('en')): errors.append('soul.json: page.de und page.en unterschiedlich aufgebaut')
    for i,b in enumerate(c['blocks']):
        if shape(b.get('de'))!=shape(b.get('en')): errors.append(f'soul.json: Block {i+1} in de und en unterschiedlich aufgebaut')
except FileNotFoundError:
    errors.append('data/soul.json fehlt')

# SOUL-Downloads müssen zu data/soul.json passen
r=subprocess.run([sys.executable,'tools/soul/build_soul.py','--check'],capture_output=True,text=True)
if r.returncode!=0: errors.append(r.stdout.strip() or 'tools/soul/build_soul.py: Prüfung fehlgeschlagen')

# Von Hand gepflegte Vorlagen: zu jeder deutschen Datei gehört eine englische
for de_path in sorted(glob.glob('layouts/partials/**/*.de.html',recursive=True)+glob.glob('layouts/partials/*/de.html')):
    en_path=re.sub(r'(^|[/.])de\.html$', lambda m: m.group(1)+'en.html', de_path)
    if not os.path.exists(en_path): errors.append(f'{de_path}: englisches Gegenstück {en_path} fehlt')

# PDF-Quelle: deutsche und englische Fassung müssen Block für Block zusammenpassen
try:
    ld=load('tools/leitfaden/content.de.json'); le=load('tools/leitfaden/content.en.json')
    bd,be=ld['blocks'],le['blocks']
    if [(b['id'],b['t']) for b in bd]!=[(b['id'],b['t']) for b in be]: errors.append('leitfaden: Block-IDs oder -Typen von de und en unterschiedlich')
    else:
        num=lambda b:sorted(re.findall(r'\d+',re.sub(r'<[^>]+>','',json.dumps({k:v for k,v in b.items() if k in('text','rows','items')},ensure_ascii=False))))
        qid=lambda b:sorted(re.findall(r'Q\d+',json.dumps(b,ensure_ascii=False)))
        for x,y in zip(bd,be):
            if num(x)!=num(y): errors.append(f"leitfaden {x['id']}: Zahlen in de und en unterschiedlich")
            if qid(x)!=qid(y): errors.append(f"leitfaden {x['id']}: Quellen-IDs in de und en unterschiedlich")
            if x['t']=='table' and [len(r) for r in x['rows']]!=[len(r) for r in y['rows']]: errors.append(f"leitfaden {x['id']}: Tabellenform unterschiedlich")
            if x['t']=='bullets' and len(x['items'])!=len(y['items']): errors.append(f"leitfaden {x['id']}: Anzahl Listenpunkte unterschiedlich")
            if x.get('urls')!=y.get('urls'): errors.append(f"leitfaden {x['id']}: Quellen-Links in de und en unterschiedlich")
        if UML.search(json.dumps(be,ensure_ascii=False).replace('Arbeitszimmer','')): errors.append('leitfaden: content.en.json enthält Umlaute')
except FileNotFoundError:
    errors.append('leitfaden: tools/leitfaden/content.*.json fehlt')

# ---------- Gebaute Seite ----------

PRIVATE = [
    (re.compile(r'(?<![\d.])(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}(?![\d.])'), 'interne IP-Adresse'),
    (re.compile(r'\b[\w-]+\.int\.kinetic-it\.de\b|\b[\w-]+\.(?:fritz\.box|lan|internal)\b'), 'interner Hostname'),
    (re.compile(r'\bWI-\d{4}\b'), 'Work-Item-Nummer'),
    (re.compile(r'\bVM ?\d{3}\b|\bLXC ?\d{3}\b'), 'VM-/LXC-Nummer'),
]

def check_built(out):
    pages={'de':os.path.join(out,'index.html'),'en':os.path.join(out,'en','index.html')}
    scans={}
    for lang,path in pages.items():
        if not os.path.exists(path): errors.append(f'{path} fehlt (Hugo-Bau unvollständig)'); return
        html=open(path,encoding='utf-8').read()
        scans[lang]=s=scan_text(html)
        if '{{' in html or 'ZgotmplZ' in html: errors.append(f'{path}: Vorlagenrest in der Ausgabe')
        if f'<html lang="{lang}"' not in html: errors.append(f'{path}: falsches lang-Attribut')
        dup={i for i in s.ids if s.ids.count(i)>1}
        if dup: errors.append(f'{path}: doppelte IDs {sorted(dup)}')
        ids=set(s.ids); base=os.path.dirname(path)
        for tag,rel,ref in s.refs:
            if ref.startswith('#'):
                if ref[1:] and ref[1:] not in ids: errors.append(f'{path}: Anker {ref} ohne Ziel')
            elif re.match(r'^(https?:|mailto:|data:)',ref):
                if ref.startswith('http:'): errors.append(f'{path}: Link ohne https: {ref}')
            else:
                target=os.path.normpath(os.path.join(base,ref.split('#')[0].split('?')[0]))
                if os.path.isdir(target): target=os.path.join(target,'index.html')
                if not os.path.exists(target): errors.append(f'{path}: {ref} zeigt auf eine Datei, die nicht gebaut wurde')
    de,en=scans['de'],scans['en']
    if de.ids!=en.ids: errors.append(f'gebaute Seiten: ids unterschiedlich: {sorted(set(de.ids)^set(en.ids))}')
    if de.nav!=en.nav: errors.append('gebaute Seiten: Anker-Links unterschiedlich')
    for t in sorted(set(de.tags)|set(en.tags)):
        if de.tags.get(t,0)!=en.tags.get(t,0): errors.append(f'gebaute Seiten: Anzahl <{t}>: de={de.tags.get(t,0)} en={en.tags.get(t,0)}')
    if UML.search(' '.join(en.text)): errors.append('en/index.html enthält Umlaute (vermutlich unübersetzter Text)')

    # Feeds und Sitemap
    n=len(d.get('history',[])); A='{http://www.w3.org/2005/Atom}'
    for f in ('feed.xml',os.path.join('en','feed.xml')):
        try:
            root=ET.parse(os.path.join(out,f)).getroot()
            entries=root.findall(A+'entry')
            if len(entries)!=n: errors.append(f'{f}: {len(entries)} Einträge, status.json history hat {n}')
            eids=[x.findtext(A+'id') for x in entries]
            if len(set(eids))!=len(eids): errors.append(f'{f}: doppelte Eintrags-IDs')
            if (root.findtext(A+'updated') or '')[:10]!=d.get('as_of'): errors.append(f'{f}: updated passt nicht zu as_of')
        except (OSError,ET.ParseError) as x:
            errors.append(f'{f}: fehlt oder kein gültiges XML ({x})')
    try:
        sm=open(os.path.join(out,'sitemap.xml'),encoding='utf-8').read(); ET.fromstring(sm)
        if sm.count('<loc>')!=2 or d.get('as_of') not in sm: errors.append('sitemap.xml: nicht genau zwei Seiten oder Datum passt nicht zu as_of')
    except (OSError,ET.ParseError) as x:
        errors.append(f'sitemap.xml: fehlt oder kein gültiges XML ({x})')
    for f in ('404.html','robots.txt',os.path.join('data','status.json')):
        if not os.path.exists(os.path.join(out,f)): errors.append(f'{f} fehlt in der gebauten Seite')

    # Typische private Angaben in allem, was als Text ausgeliefert wird
    for path in sorted(glob.glob(os.path.join(out,'**','*'),recursive=True)):
        if not path.endswith(('.html','.xml','.json','.md','.txt')): continue
        txt=open(path,encoding='utf-8',errors='replace').read()
        for rx,what in PRIVATE:
            m=rx.search(txt)
            if m: errors.append(f'{path}: {what} in der Ausgabe ("{m.group(0)}")')

built=len(sys.argv)>1
if built:
    check_built(sys.argv[1])

if errors:
    print('Prüfung FEHLGESCHLAGEN'); [print(' -',x) for x in errors]; sys.exit(1)
print('Prüfung OK: Quellen vollständig und in beiden Sprachen gleich aufgebaut' + ('; gebaute Seite: IDs, Anker, Links, Feeds, Sitemap in Ordnung, keine typischen privaten Angaben' if built else ''))
