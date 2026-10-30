#!/usr/bin/env python3
"""Vergleicht die von Hugo gebauten Seiten mit den bisherigen Seiten (index.html, en/index.html, Feeds).

Während der Umstellung gelten die bisherigen Dateien als Referenz. Verglichen werden Tags, Attribute und Text,
nicht die Schreibweise: Entities werden aufgelöst, Leerraum zusammengefasst, Kommentare ignoriert, JSON-LD als JSON.
Aufruf:  hugo --destination /tmp/out && python3 tools/hugo_parity.py /tmp/out
Exit 1 bei Abweichungen; die ersten Unterschiede werden mit Abschnitts-ID angezeigt.
"""
import difflib, json, re, sys
from html.parser import HTMLParser

class Tok(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.t, self.stack, self.sec, self.buf = [], [], '', []
        self.pre = 0
    def flush(self):
        if not self.buf: return
        s = ''.join(self.buf); self.buf = []
        if not self.pre: s = re.sub(r'\s+', ' ', s).strip()
        if s: self.t.append(('text', s, self.sec))
    def handle_starttag(self, tag, attrs):
        self.flush()
        a = tuple(sorted((k, re.sub(r'\s+', ' ', v or '').strip()) for k, v in attrs))
        d = dict(a)
        if tag in ('section',) and d.get('id'): self.sec = d['id']
        if tag == 'div' and d.get('id') == 'start': self.sec = 'start'
        if tag == 'header': self.sec = 'header'
        if tag == 'footer': self.sec = 'footer'
        if tag == 'head': self.sec = 'head'
        if tag == 'pre': self.pre += 1
        if tag == 'script': self.script = d.get('type', 'js')
        self.t.append(('<' + tag, a, self.sec))
    def handle_endtag(self, tag):
        self.flush()
        if tag == 'pre': self.pre -= 1
        self.t.append(('</' + tag, '', self.sec))
    def handle_data(self, data):
        self.buf.append(data)
    handle_startendtag = handle_starttag

def tokens(html):
    p = Tok(); p.feed(html); p.flush()
    out = []
    for i, (k, v, sec) in enumerate(p.t):
        if k == 'text' and i and p.t[i-1][0] == '<script' and dict(p.t[i-1][1]).get('type') == 'application/ld+json':
            v = json.dumps(json.loads(v), sort_keys=True)
        out.append((k, v, sec))
    return out

def compare(name, a, b, kind):
    if kind == 'html':
        ta, tb = tokens(a), tokens(b)
    else:   # Feeds: Leerraum zwischen Tags ignorieren
        norm = lambda s: re.sub(r'>\s+<', '><', re.sub(r'\s+', ' ', s)).strip()
        ta, tb = [norm(a)], [norm(b)]
    key = lambda t: t[:2] if isinstance(t, tuple) else t
    sm = difflib.SequenceMatcher(None, [key(x) for x in ta], [key(x) for x in tb], autojunk=False)
    diffs = [o for o in sm.get_opcodes() if o[0] != 'equal']
    if not diffs: return 0
    print('%s: %d Abweichung(en)' % (name, len(diffs)))
    for tag, i1, i2, j1, j2 in diffs[:12]:
        sec = (ta[i1][2] if kind == 'html' and i1 < len(ta) else (tb[j1][2] if kind == 'html' and j1 < len(tb) else ''))
        print('  [%s] Abschnitt %r\n    alt : %s\n    neu : %s' % (tag, sec, str([key(x) for x in ta[i1:i2][:3]])[:300], str([key(x) for x in tb[j1:j2][:3]])[:300]))
    return len(diffs)

def main():
    out = sys.argv[1].rstrip('/') + '/'
    n = 0
    for ref, new, kind in (('index.html', 'index.html', 'html'), ('en/index.html', 'en/index.html', 'html'),
                           ('feed.xml', 'feed.xml', 'xml'), ('en/feed.xml', 'en/feed.xml', 'xml'),
                           ('sitemap.xml', 'sitemap.xml', 'xml')):
        n += compare(ref, open(ref, encoding='utf-8').read(), open(out + new, encoding='utf-8').read(), kind)
    print('Hugo-Vergleich: ' + ('ABWEICHUNGEN' if n else 'OK, gleich'))
    sys.exit(1 if n else 0)

main()
