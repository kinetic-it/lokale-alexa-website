#!/usr/bin/env python3
"""Erzeugt den Abschnitt "So haben wir unseren Echo 2 umgebaut" (<section id="umbau">) in beiden Seiten
aus tools/umbau/content.json (Deutsch und Englisch je Block, gleiche Struktur).
Inline: `code`, **fett**, [Text](Link). Bilder liegen in images/ (EN-Seite: ../images/).
Aufruf im Repo-Wurzelverzeichnis:
  python3 tools/umbau/build_umbau.py          # schreibt index.html und en/index.html
  python3 tools/umbau/build_umbau.py --check  # Exit 1, wenn Seiten und Quelle nicht zusammenpassen
"""
import html, json, os, re, sys

E = html.escape
C = json.load(open('tools/umbau/content.json', encoding='utf-8'))
ISSUE = 'https://github.com/kinetic-it/lokale-alexa-website/issues/new?template=testbericht.md'

def inline(s):
    s = E(s, quote=False)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: '<a href="%s">%s</a>' % (E(m.group(2)), m.group(1)), s)

def effort(b, p):
    n, to = b['effort'], b.get('to', b['effort'])
    dots = ''.join('<i class="%s"></i>' % ('on' if i <= n else ('rng' if i <= to else '')) for i in range(1, 6))
    val = ('%d %s %d %s' % (n, p['effort_to'], to, p['effort_word'])) if to != n else ('%d %s' % (n, p['effort_word']))
    return ('<p class="eff"><span class="dots" aria-hidden="true">%s</span> <strong>%s: %s</strong> %s</p>'
            % (dots, E(p['effort_label']), val, inline(b['text'])))

def block(b, p):
    if isinstance(b, str): return '<p>%s</p>' % inline(b)
    if 'ul' in b: return '<ul>%s</ul>' % ''.join('<li>%s</li>' % inline(x) for x in b['ul'])
    if 'ol' in b: return '<ol>%s</ol>' % ''.join('<li>%s</li>' % inline(x) for x in b['ol'])
    if 'effort' in b: return effort(b, p)
    if 'links' in b: return '<ul class="srcs">%s</ul>' % ''.join('<li><a href="%s">%s</a></li>' % (E(u), E(t)) for t, u in b['links'])
    if 'table' in b:
        h = p['table_head']
        rows = ''.join('<tr><td data-l="%s">%s</td><td data-l="%s">%s</td><td data-l="%s"><span class="ev ev-%s">%s</span></td></tr>'
                       % (E(h[0]), inline(a), E(h[1]), inline(s), E(h[2]), k, E(p['ev'][k])) for a, s, k in b['table'])
        return ('<div class="tablewrap" tabindex="0" role="region" aria-label="%s"><table class="stack"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
                % (E(p['steps'][-1]['title']), ''.join('<th>%s</th>' % E(x) for x in h), rows))
    raise ValueError(b)

def section(lang):
    p = C[lang]
    pre = '../' if lang == 'en' else ''
    o = ['<section id="umbau">', '  <div class="wrap">',
         '    <div class="eyebrow">%s</div>' % E(p['eyebrow']),
         '    <h2>%s</h2>' % E(p['h2']),
         '    <p class="intro">%s</p>' % inline(p['intro']),
         '    <div class="warnbox" role="note" aria-labelledby="warn-t">',
         '      <p class="warn-big" id="warn-t">%s</p>' % E(p['warn_title'])]
    o += ['      <p>%s</p>' % inline(x) for x in p['warn_p']]
    o += ['      <p class="warn-sub">%s</p>' % E(p['warn_third_title']),
          '      <ul>%s</ul>' % ''.join('<li>%s</li>' % inline(x) for x in p['warn_third']),
          '    </div>',
          '    <div class="ulegend">',
          '      <h3>%s</h3>' % E(p['legend_title']),
          '      <p>%s</p>' % E(p['legend_ev_intro']),
          '      <p class="evs">%s</p>' % ' '.join('<span class="ev ev-%s">%s</span>' % (k, E(v)) for k, v in p['ev'].items()),
          '      <p>%s</p>' % E(p['legend_scale']),
          '    </div>',
          '    <nav class="utoc" aria-label="%s">' % E(p['toc_title']),
          '      <h3>%s</h3>' % E(p['toc_title']),
          '      <ol>%s</ol>' % ''.join('<li><a href="#%s">%s</a></li>' % (s['id'], E(s['title'])) for s in p['steps']),
          '    </nav>']
    for n, s in enumerate(p['steps'], 1):
        o += ['    <article class="ustep" id="%s">' % s['id'],
              '      <p class="unum">%s %d</p>' % (E(p['step_word']), n),
              '      <h3>%s</h3>' % E(s['title']),
              '      <p class="evs">%s</p>' % ' '.join('<span class="ev ev-%s">%s</span>' % (k, E(p['ev'][k])) for k in s['tags'])]
        if s.get('warn'):
            o.append('      <p class="warn-mini"><strong>%s.</strong> %s</p>' % (E(p['warn_title']), E(p['warn_mini'])))
        if s.get('figs'):
            o.append('      <div class="ufigs">')
            for f in s['figs']:
                o.append('        <figure class="ufig"><img src="%simages/%s" width="%d" height="%d" alt="%s" loading="lazy"><figcaption>%s</figcaption></figure>'
                         % (pre, f['src'], f['w'], f['h'], E(f['alt']), E(f['cap'])))
            o.append('      </div>')
            o.append('      <p class="small">%s</p>' % E(p['fig_credit']))
        o.append('      <dl>')
        for fld in s['fields']:
            o.append('        <dt>%s</dt><dd>%s</dd>' % (E(p['labels'][fld['k']]), ''.join(block(b, p) for b in fld['b'])))
        o += ['      </dl>', '    </article>']
    o += ['    <div class="callout"><p>%s <a href="%s">%s</a></p></div>' % (E(p['closing']), ISSUE, E(p['closing_link'])),
          '  </div>', '</section>']
    return '\n'.join(o)

def verify():
    d, e = C['de'], C['en']
    errs = []
    if [s['id'] for s in d['steps']] != [s['id'] for s in e['steps']]: errs.append('Etappen-IDs von de und en unterschiedlich')
    for a, b in zip(d['steps'], e['steps']):
        if a['tags'] != b['tags'] or a.get('warn') != b.get('warn'): errs.append('%s: Kennzeichen/Warnung unterschiedlich' % a['id'])
        if [f['k'] for f in a['fields']] != [f['k'] for f in b['fields']]: errs.append('%s: Felder unterschiedlich' % a['id'])
        if [(f['src'], f['w'], f['h']) for f in a.get('figs', [])] != [(f['src'], f['w'], f['h']) for f in b.get('figs', [])]: errs.append('%s: Bilder unterschiedlich' % a['id'])
        for fa, fb in zip(a['fields'], b['fields']):
            shape = lambda bl: [('s' if isinstance(x, str) else next(iter(x)),
                                 len(x[next(iter(x))]) if not isinstance(x, str) and isinstance(x[next(iter(x))], list) else 0) for x in bl]
            if shape(fa['b']) != shape(fb['b']): errs.append('%s/%s: Blockform de/en unterschiedlich' % (a['id'], fa['k']))
    if re.search('[äöüßÄÖÜ]', json.dumps(e, ensure_ascii=False)): errs.append('Umlaute im englischen Text')
    for lang in ('de', 'en'):
        for s in C[lang]['steps']:
            for f in s.get('figs', []):
                if not os.path.exists('images/' + f['src']): errs.append('Bild fehlt: ' + f['src'])
    return errs

def apply(s, lang):
    a, b = '<!-- umbau:start -->', '<!-- umbau:end -->'
    i, j = s.index(a) + len(a), s.index(b)
    return s[:i] + '\n' + section(lang) + '\n' + s[j:]

def main():
    errs = verify()
    if errs:
        print('umbau: ' + '; '.join(errs)); sys.exit(1)
    check = '--check' in sys.argv
    ok = True
    for lang, path in (('de', 'index.html'), ('en', 'en/index.html')):
        s = open(path, encoding='utf-8').read()
        new = apply(s, lang)
        if check: ok &= new == s
        else: open(path, 'w', encoding='utf-8').write(new)
    if check and not ok:
        print('umbau: Seiten passen nicht zu content.json (python3 tools/umbau/build_umbau.py)'); sys.exit(1)
    print('umbau: OK' if check else 'umbau: geschrieben')

main()
