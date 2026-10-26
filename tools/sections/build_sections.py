#!/usr/bin/env python3
"""Erzeugt zweisprachige Seitenteile aus einer Quelle:
  - Abschnitt "Nachbauen" (<section id="nachbauen">) aus tools/sections/steps.json
  - Verlauf im Abschnitt "Stand" (statischer Fallback) aus data/status.json -> history
Aufruf im Repo-Wurzelverzeichnis:
  python3 tools/sections/build_sections.py          # schreibt index.html und en/index.html
  python3 tools/sections/build_sections.py --check  # Exit 1, wenn die Seiten nicht zur Quelle passen
"""
import html, json, sys

E = html.escape
STEPS = json.load(open('tools/sections/steps.json', encoding='utf-8'))
STATUS = json.load(open('data/status.json', encoding='utf-8'))
ISSUE = 'https://github.com/kinetic-it/lokale-alexa-website/issues/new?template=testbericht.md'
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def fmt(d, lang):
    y, m, t = d.split('-')
    return '%d %s %s' % (int(t), MON[int(m) - 1], y) if lang == 'en' else '%s.%s.%s' % (t, m, y)

def steps(lang):
    p = STEPS[lang]
    items = []
    for n, (h, txt, ref) in enumerate(p['steps'], 1):
        items.append('      <li class="step"><span class="label">%s %d</span><h3>%s</h3><p>%s</p><p class="ref">%s</p></li>'
                     % (E(p['step']), n, E(h), E(txt), E(ref)))
    return '\n'.join([
        '<section id="nachbauen" class="alt">',
        '  <div class="wrap">',
        '    <div class="eyebrow">%s</div>' % E(p['eyebrow']),
        '    <h2>%s</h2>' % E(p['h2']),
        '    <p class="intro">%s</p>' % E(p['intro']),
        '    <ol class="steps">',
        *items,
        '    </ol>',
        '    <div class="callout"><p>%s <a href="%s">%s</a></p></div>' % (E(p['callout']), ISSUE, E(p['callout_link'])),
        '  </div>',
        '</section>'])

def history(lang):
    h = STATUS.get('history', [])
    texts = STATUS['en']['history'] if lang == 'en' else [x['text'] for x in h]
    return '\n'.join('          <li><time datetime="%s">%s</time><span>%s</span></li>' % (x['date'], fmt(x['date'], lang), E(t))
                     for x, t in zip(h, texts))

PARTS = {'nachbauen': steps, 'history': history}

def apply(s, lang):
    for key, fn in PARTS.items():
        a, b = '<!-- %s:start -->' % key, '<!-- %s:end -->' % key
        i, j = s.index(a) + len(a), s.index(b)
        s = s[:i] + '\n' + fn(lang) + '\n' + s[j:]
    return s

def main():
    check = '--check' in sys.argv
    ok = True
    for lang, path in (('de', 'index.html'), ('en', 'en/index.html')):
        s = open(path, encoding='utf-8').read()
        new = apply(s, lang)
        if check: ok &= new == s
        else: open(path, 'w', encoding='utf-8').write(new)
    if check and not ok:
        print('sections: Seiten passen nicht zu steps.json / status.json (python3 tools/sections/build_sections.py)'); sys.exit(1)
    print('sections: OK' if check else 'sections: geschrieben')

main()
