#!/usr/bin/env python3
"""Prüft, dass die deutsche (index.html) und die englische Seite (en/index.html)
denselben Aufbau haben und dass data/status.json beide Sprachen vollständig enthält.
Aufruf im Repo-Wurzelverzeichnis: python3 tools/check_i18n.py
Exit 0 = gleich aufgebaut, Exit 1 = Abweichung (wird ausgegeben)."""
import json, re, sys
from html.parser import HTMLParser

class Scan(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.tags={}; self.nav=[]; self.in_script=False; self.text=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs); self.tags[tag]=self.tags.get(tag,0)+1
        if a.get('id'): self.ids.append(a['id'])
        if tag=='a' and a.get('href','').startswith('#'): self.nav.append(a['href'])
        if tag in('script','style'): self.in_script=True
    def handle_endtag(self, tag):
        if tag in('script','style'): self.in_script=False
    def handle_data(self, d):
        if not self.in_script: self.text.append(d)

def scan(path):
    s=Scan(); s.feed(open(path,encoding='utf-8').read()); return s

errors=[]
de, en = scan('index.html'), scan('en/index.html')
if de.ids!=en.ids: errors.append(f'ids unterschiedlich: {set(de.ids)^set(en.ids)}')
if de.nav!=en.nav: errors.append('Anker-Links unterschiedlich')
for t in sorted(set(de.tags)|set(en.tags)):
    if de.tags.get(t,0)!=en.tags.get(t,0): errors.append(f'Anzahl <{t}>: de={de.tags.get(t,0)} en={en.tags.get(t,0)}')
if re.search(r'[äöüÄÖÜß]',' '.join(en.text)): errors.append('en/index.html enthält Umlaute (vermutlich unübersetzter Text)')

d=json.load(open('data/status.json',encoding='utf-8')); e=d.get('en')
if not e: errors.append('status.json: Objekt "en" fehlt')
else:
    for k in ('title','evidence'):
        if not e.get(k): errors.append(f'status.json en.{k} fehlt')
    for k in ('confirmed','not_yet_verified','known_issues','history'):
        if len(e.get(k,[]))!=len(d.get(k,[])): errors.append(f'status.json {k}: de={len(d.get(k,[]))} en={len(e.get(k,[]))}')
    ids={m['id'] for m in d['milestones']}
    if ids!=set(e.get('milestones',{})): errors.append(f'status.json en.milestones passt nicht zu den IDs {sorted(ids)}')

# Generierte Seitenteile (SOUL-Beispiel, Nachbauen, Verlauf) müssen zu ihren Quellen passen
import subprocess
for gen in ('tools/soul/build_soul.py','tools/sections/build_sections.py'):
    r=subprocess.run([sys.executable,gen,'--check'],capture_output=True,text=True)
    if r.returncode!=0: errors.append(r.stdout.strip() or gen+': Prüfung fehlgeschlagen')

# PDF-Quelle: deutsche und englische Fassung müssen Block für Block zusammenpassen
try:
    ld=json.load(open('tools/leitfaden/content.de.json',encoding='utf-8')); le=json.load(open('tools/leitfaden/content.en.json',encoding='utf-8'))
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
        if re.search(r'[äöüÄÖÜß]',json.dumps(be,ensure_ascii=False).replace('Arbeitszimmer','')): errors.append('leitfaden: content.en.json enthält Umlaute')
except FileNotFoundError:
    errors.append('leitfaden: tools/leitfaden/content.*.json fehlt')

if errors:
    print('i18n-Prüfung FEHLGESCHLAGEN'); [print(' -',x) for x in errors]; sys.exit(1)
print('i18n-Prüfung OK: gleiche IDs, Anker, Tag-Anzahlen, status.json und PDF-Quelle vollständig')
