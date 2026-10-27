#!/usr/bin/env python3
"""Atom-Feeds aus data/status.json -> history (de: feed.xml, en: en/feed.xml).
Aufruf: python3 tools/feed/build_feed.py [--check]"""
import json, sys
from xml.sax.saxutils import escape as E

BASE = 'https://kinetic-it.github.io/lokale-alexa-website/'
S = json.load(open('data/status.json', encoding='utf-8'))
L = {
    'de': {'path': 'feed.xml', 'page': BASE, 'title': 'Lokale Alexa: Projektverlauf',
           'sub': 'Neue Einträge im öffentlichen Projektverlauf. Berichtet ist nicht gleich getestet ist nicht gleich abgenommen.'},
    'en': {'path': 'en/feed.xml', 'page': BASE + 'en/', 'title': 'Local Alexa: project history',
           'sub': 'New entries in the public project history. Reported is not tested is not accepted.'},
}

def feed(lang):
    p = L[lang]
    hist = S['history']
    texts = S['en']['history'] if lang == 'en' else [h['text'] for h in hist]
    seen, entries = {}, []
    for h, t in zip(hist, texts):
        n = seen[h['date']] = seen.get(h['date'], 0) + 1
        entries.append((h['date'], n, t))
    out = ['<?xml version="1.0" encoding="utf-8"?>',
           '<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="%s">' % lang,
           '  <title>%s</title>' % E(p['title']),
           '  <subtitle>%s</subtitle>' % E(p['sub']),
           '  <id>%s%s</id>' % (BASE, p['path']),
           '  <link rel="self" type="application/atom+xml" href="%s%s"/>' % (BASE, p['path']),
           '  <link rel="alternate" type="text/html" href="%s"/>' % p['page'],
           '  <updated>%sT00:00:00Z</updated>' % S['as_of'],
           '  <author><name>kinetic-it</name></author>']
    for d, n, t in reversed(entries):
        out += ['  <entry>',
                '    <title>%s</title>' % E(t if len(t) <= 90 else t[:87].rstrip() + '...'),
                '    <id>tag:kinetic-it.github.io,2026:lokale-alexa/%s/%s-%d</id>' % (lang, d, n),
                '    <link rel="alternate" type="text/html" href="%s#stand"/>' % p['page'],
                '    <updated>%sT00:00:00Z</updated>' % d,
                '    <summary>%s</summary>' % E(t),
                '  </entry>']
    return '\n'.join(out + ['</feed>']) + '\n'

def main():
    check = '--check' in sys.argv
    ok = True
    for lang in L:
        new = feed(lang)
        path = L[lang]['path']
        if check:
            try: ok &= open(path, encoding='utf-8').read() == new
            except FileNotFoundError: ok = False
        else: open(path, 'w', encoding='utf-8').write(new)
    if check and not ok:
        print('feed: feed.xml passt nicht zu status.json (python3 tools/feed/build_feed.py)'); sys.exit(1)
    print('feed: OK' if check else 'feed: geschrieben')

main()
