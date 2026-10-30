#!/usr/bin/env python3
"""Erzeugt aus data/soul.json
  - downloads/SOUL-beispiel.md und downloads/SOUL-example.md
  - den Abschnitt <section id="soul"> in index.html und en/index.html (zwischen den Markern)
Aufruf im Repo-Wurzelverzeichnis:
  python3 tools/soul/build_soul.py          # schreibt
  python3 tools/soul/build_soul.py --check  # Exit 1, wenn Dateien nicht zur Quelle passen
"""
import html, json, sys

C = json.load(open('data/soul.json', encoding='utf-8'))
START, END = '<!-- soul:start -->', '<!-- soul:end -->'
E = html.escape

def md(lang):
    parts = ['\n'.join(b[lang]['lines']) for b in C['blocks']]
    return '\n\n'.join(parts) + '\n'

def section(lang):
    p = C['page'][lang]
    pre = '.' if lang == 'de' else '..'
    name = C['file_names'][lang]
    rows = []
    for b in C['blocks']:
        t = b[lang]
        rows.append('      <div class="srow"><pre class="sfile"><code>%s</code></pre><div class="swhy"><span class="label">%s</span><p>%s</p></div></div>'
                    % (E('\n'.join(t['lines'])), E(t['title']), E(t['why'])))
    cards = ['      <div class="card"><span class="label">%s</span><h3>%s</h3><p>%s</p></div>' % (E(a), E(b), E(c)) for a, b, c in p['cards']]
    return '\n'.join([
        START,
        '<section id="soul">',
        '  <div class="wrap">',
        '    <div class="eyebrow">%s</div>' % E(p['eyebrow']),
        '    <h2>%s</h2>' % E(p['h2']),
        '    <p class="intro">%s</p>' % E(p['intro']),
        '    <div class="soul">',
        '      <div class="shead"><span>%s</span><span>%s</span></div>' % (E(p['head_file']), E(p['head_why'])),
        *rows,
        '    </div>',
        '    <p style="margin-top:22px"><a class="button" href="%s/downloads/%s" download>%s</a></p>' % (pre, E(name), E(p['button'])),
        '    <div class="grid two">',
        *cards,
        '    </div>',
        '    <div class="callout"><p>%s <a href="%s">%s</a></p></div>' % (E(p['callout']), E(C['doc_url']), E(p['doc_link'])),
        '  </div>',
        '</section>',
        END])

def inject(path, lang, check):
    s = open(path, encoding='utf-8').read()
    i, j = s.index(START), s.index(END) + len(END)
    new = s[:i] + section(lang) + s[j:]
    if check: return new == s
    open(path, 'w', encoding='utf-8').write(new); return True

def main():
    check = '--check' in sys.argv
    ok = True
    for lang, path in (('de', 'index.html'), ('en', 'en/index.html')):
        ok &= inject(path, lang, check)
        f = 'downloads/' + C['file_names'][lang]
        if check:
            try: ok &= open(f, encoding='utf-8').read() == md(lang)
            except FileNotFoundError: ok = False
        else: open(f, 'w', encoding='utf-8').write(md(lang))
    if check and not ok:
        print('soul: Seiten oder Downloads passen nicht zu data/soul.json (python3 tools/soul/build_soul.py)'); sys.exit(1)
    print('soul: OK' if check else 'soul: geschrieben')

main()
