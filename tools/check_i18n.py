#!/usr/bin/env python3
"""Prüft die Quellen der Seite und, wenn ein Ausgabeordner angegeben ist, die von Hugo gebaute Seite.

Aufruf im Repo-Wurzelverzeichnis:
  python3 tools/check_i18n.py            # nur Quellen (data/, layouts/, downloads/, PDF-Quelle)
  python3 tools/check_i18n.py public     # zusätzlich die gebaute Seite im Ordner public/

Quellen: Deutsch und Englisch vollständig und gleich aufgebaut, gültige Befunde, Downloads passen zur Quelle.
Gebaute Seite (alle Seiten, paarweise Deutsch/Englisch): gleiche IDs, Anker und Tag-Anzahlen, kein deutscher Rest
im Englischen, genau eine <h1>, eigener Titel und Beschreibung je Seite, alle internen Links und Sprungmarken haben
ein Ziel (auch seitenübergreifend), Feeds und Sitemap passen zu den Daten und Seiten, keine Vorlagenreste,
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
for name in ('steps','umbau','warum'):
    try:
        c=load(f'data/{name}.json')
        if shape(c.get('de'))!=shape(c.get('en')): errors.append(f'{name}.json: Aufbau von de und en unterschiedlich')
    except FileNotFoundError:
        errors.append(f'data/{name}.json fehlt')
try:
    w=load('data/warum.json')
    if shape(w.get('de'))!=shape(w.get('en')): errors.append('warum.json: Aufbau von de und en unterschiedlich')
    kennzeichen=set(load('data/umbau.json')['de']['ev'])
    for lang in ('de','en'):
        for i,row in enumerate(w[lang]['table']['rows']):
            if row[2] not in kennzeichen or row[4] not in kennzeichen: errors.append(f'warum.json {lang}: Zeile {i+1} hat ein unbekanntes Kennzeichen')
except FileNotFoundError:
    errors.append('data/warum.json fehlt')
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

# Seiten: zu jeder deutschen Inhaltsdatei gehört eine englische mit denselben Abschnitten
for de_path in sorted(glob.glob('content/*.de.md')):
    en_path=de_path[:-len('.de.md')]+'.en.md'
    if not os.path.exists(en_path): errors.append(f'{de_path}: englisches Gegenstück {en_path} fehlt'); continue
    sec=lambda f: re.findall(r'^sections: (.*)$',open(f,encoding='utf-8').read(),re.M)
    if not sec(de_path) or sec(de_path)!=sec(en_path): errors.append(f'{de_path}: Feld sections fehlt oder ist in de und en unterschiedlich')
    for f in (de_path,en_path):
        fm=open(f,encoding='utf-8').read()
        for k in ('title','description'):
            if not re.search(rf'^{k}: "[^"]+',fm,re.M): errors.append(f'{f}: {k} fehlt')
    if UML.search(open(en_path,encoding='utf-8').read()): errors.append(f'{en_path}: Umlaute im englischen Text')

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
    from urllib.parse import urlparse
    root=os.path.join(out,'index.html')
    if not os.path.exists(root): errors.append(f'{root} fehlt (Hugo-Bau unvollständig)'); return
    m=re.search(r'<link rel="canonical" href="([^"]+)"',open(root,encoding='utf-8').read())
    if not m: errors.append(f'{root}: canonical fehlt'); return
    site=m.group(1); base=urlparse(site).path          # z. B. /lokale-alexa-website/
    def to_file(url):
        """Adresse der eigenen Seite (absolut oder ab Wurzel) -> Datei im Ausgabeordner, sonst None."""
        path=urlparse(url).path if url.startswith(site) else (url if url.startswith(base) else None)
        if path is None: return None
        f=os.path.normpath(os.path.join(out,path[len(base):]))
        return os.path.join(f,'index.html') if os.path.isdir(f) or path.endswith('/') else f

    # Alle Seiten einlesen (Weiterleitungsseiten und 404 gehören nicht dazu)
    pages={}
    for path in sorted(glob.glob(os.path.join(out,'**','index.html'),recursive=True)):
        html=open(path,encoding='utf-8').read()
        if 'http-equiv="refresh"' in html or 'http-equiv=refresh' in html: continue
        pages[os.path.normpath(path)]=(html,scan_text(html))
    titles={}
    for path,(html,s) in pages.items():
        if '{{' in html or 'ZgotmplZ' in html: errors.append(f'{path}: Vorlagenrest in der Ausgabe')
        lang=re.search(r'<html lang="(\w+)"',html); lang=lang.group(1) if lang else ''
        want='en' if os.path.relpath(path,out).split(os.sep)[0]=='en' else 'de'
        if lang!=want: errors.append(f'{path}: lang-Attribut ist "{lang}", erwartet "{want}"')
        dup={i for i in s.ids if s.ids.count(i)>1}
        if dup: errors.append(f'{path}: doppelte IDs {sorted(dup)}')
        if s.tags.get('h1',0)!=1: errors.append(f'{path}: {s.tags.get("h1",0)} Überschriften <h1>, erwartet genau eine')
        t=re.search(r'<title>([^<]*)</title>',html); t=t.group(1) if t else ''
        if not t or t in titles: errors.append(f'{path}: Seitentitel fehlt oder ist doppelt ("{t}")')
        titles[t]=path
        if not re.search(r'<meta name="description" content="[^"]{40,}"',html): errors.append(f'{path}: Beschreibung fehlt oder ist zu kurz')
        c=re.search(r'<link rel="canonical" href="([^"]+)"',html)
        if not c or os.path.normpath(to_file(c.group(1)) or '')!=path: errors.append(f'{path}: canonical zeigt nicht auf die Seite selbst')
        if want=='en' and UML.search(' '.join(s.text)): errors.append(f'{path}: Umlaute im englischen Text (vermutlich unübersetzt)')
        ids=set(s.ids); here=os.path.dirname(path)
        for tag,rel,ref in s.refs:
            if ref.startswith('#'):
                if ref[1:] and ref!='#top' and ref[1:] not in ids: errors.append(f'{path}: Anker {ref} ohne Ziel')
                continue
            if ref.startswith(('mailto:','data:')): continue
            if ref.startswith('http:'): errors.append(f'{path}: Link ohne https: {ref}'); continue
            target=to_file(ref)
            if target is None:
                if ref.startswith('https:'): continue                      # externer Link, wird nicht geprüft
                if ref.startswith('/'): errors.append(f'{path}: {ref} liegt außerhalb von {base}'); continue
                target=os.path.normpath(os.path.join(here,ref.split('#')[0].split('?')[0]))
                if os.path.isdir(target): target=os.path.join(target,'index.html')
            target=os.path.normpath(target.split('#')[0])
            if not os.path.exists(target): errors.append(f'{path}: {ref} zeigt auf eine Datei, die nicht gebaut wurde'); continue
            frag=urlparse(ref).fragment
            if frag and target in pages and frag not in pages[target][1].ids: errors.append(f'{path}: {ref} zeigt auf eine Sprungmarke, die es dort nicht gibt')

    # Deutsch und Englisch paarweise: gleiche IDs, Anker und Tag-Anzahlen
    pairs=0
    for path,(html,de) in pages.items():
        if os.path.relpath(path,out).split(os.sep)[0]=='en': continue
        alt=re.search(r'<link rel="alternate" hreflang="en" href="([^"]+)"',html)
        other=os.path.normpath(to_file(alt.group(1)) or '') if alt else ''
        if other not in pages: errors.append(f'{path}: englische Fassung fehlt'); continue
        pairs+=1; en=pages[other][1]; name=os.path.relpath(path,out)
        if de.ids!=en.ids: errors.append(f'{name}: ids in de und en unterschiedlich: {sorted(set(de.ids)^set(en.ids))}')
        if de.nav!=en.nav: errors.append(f'{name}: Anker-Links in de und en unterschiedlich')
        for t in sorted(set(de.tags)|set(en.tags)):
            if de.tags.get(t,0)!=en.tags.get(t,0): errors.append(f'{name}: Anzahl <{t}>: de={de.tags.get(t,0)} en={en.tags.get(t,0)}')
    if pairs*2!=len(pages): errors.append(f'{len(pages)} Seiten, aber nur {pairs} Sprachpaare')

    # Feeds (Verlauf und Befunde) und Sitemap
    try: findings=load('data/findings.json')['entries']
    except (OSError,KeyError): findings=[]
    n=len(d.get('history',[]))+len(findings); A='{http://www.w3.org/2005/Atom}'
    newest=max([h['date'] for h in d.get('history',[])]+[f['date'] for f in findings] or [''])
    for f in ('feed.xml',os.path.join('en','feed.xml')):
        try:
            rootx=ET.parse(os.path.join(out,f)).getroot()
            entries=rootx.findall(A+'entry')
            if len(entries)!=n: errors.append(f'{f}: {len(entries)} Einträge, Verlauf und Befunde haben zusammen {n}')
            eids=[x.findtext(A+'id') for x in entries]
            if len(set(eids))!=len(eids): errors.append(f'{f}: doppelte Eintrags-IDs')
            ups=[x.findtext(A+'updated') for x in entries]
            if ups!=sorted(ups,reverse=True): errors.append(f'{f}: Einträge nicht neueste zuerst')
            if (rootx.findtext(A+'updated') or '')[:10]!=newest: errors.append(f'{f}: updated passt nicht zum neuesten Eintrag')
            for x in entries:
                href=x.find(A+'link').get('href'); target=to_file(href)
                tp=os.path.normpath((target or '').split('#')[0])
                if tp not in pages or urlparse(href).fragment not in pages[tp][1].ids: errors.append(f'{f}: Eintrag verweist auf {href}, das Ziel gibt es nicht')
        except (OSError,ET.ParseError) as x:
            errors.append(f'{f}: fehlt oder kein gültiges XML ({x})')
    try:
        sm=open(os.path.join(out,'sitemap.xml'),encoding='utf-8').read(); ET.fromstring(sm)
        locs=re.findall(r'<loc>([^<]+)</loc>',sm)
        if sorted(os.path.normpath(to_file(u) or '') for u in locs)!=sorted(pages): errors.append('sitemap.xml: Einträge passen nicht zu den gebauten Seiten')
        if d.get('as_of') not in sm: errors.append('sitemap.xml: Datum passt nicht zu as_of')
    except (OSError,ET.ParseError) as x:
        errors.append(f'sitemap.xml: fehlt oder kein gültiges XML ({x})')
    for f in ('404.html','robots.txt',os.path.join('data','status.json')):
        if not os.path.exists(os.path.join(out,f)): errors.append(f'{f} fehlt in der gebauten Seite')

    # Typische private Angaben in allem, was als Text ausgeliefert wird
    for path in sorted(glob.glob(os.path.join(out,'**','*'),recursive=True)):
        if not path.endswith(('.html','.xml','.json','.md','.txt')): continue
        txt=open(path,encoding='utf-8',errors='replace').read()
        for rx,what in PRIVATE:
            mm=rx.search(txt)
            if mm: errors.append(f'{path}: {what} in der Ausgabe ("{mm.group(0)}")')
    return len(pages)

built=len(sys.argv)>1
count=check_built(sys.argv[1]) if built else 0

if errors:
    print('Prüfung FEHLGESCHLAGEN'); [print(' -',x) for x in errors]; sys.exit(1)
print('Prüfung OK: Quellen vollständig und in beiden Sprachen gleich aufgebaut' + (f'; gebaute Seite: {count} Seiten, IDs, Anker, Links, Feeds, Sitemap in Ordnung, keine typischen privaten Angaben' if built else ''))
