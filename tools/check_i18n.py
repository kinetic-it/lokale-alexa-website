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
    for k in ('confirmed','not_yet_verified','known_issues'):
        if len(e.get(k,[]))!=len(d.get(k,[])): errors.append(f'status.json {k}: de={len(d.get(k,[]))} en={len(e.get(k,[]))}')
    ids={m['id'] for m in d['milestones']}
    if ids!=set(e.get('milestones',{})): errors.append(f'status.json en.milestones passt nicht zu den IDs {sorted(ids)}')

if errors:
    print('i18n-Prüfung FEHLGESCHLAGEN'); [print(' -',x) for x in errors]; sys.exit(1)
print('i18n-Prüfung OK: gleiche IDs, Anker, Tag-Anzahlen und status.json vollständig')
