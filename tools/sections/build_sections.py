#!/usr/bin/env python3
"""Erzeugt zweisprachige Seitenteile aus einer Quelle:
  - JSON-LD im Kopf (dateModified aus status.json -> as_of)
  - Abschnitt "Nachbauen" (<section id="nachbauen">) aus data/steps.json
  - Abschnitt "Befunde und Erkenntnisse" aus data/findings.json
  - statischer Fallback des Projektstands aus data/status.json: Kopfkarte (Titel, Datum, Meilensteine,
    letzter Test), Listen "berichtet / offen / Probleme" und Verlauf. Das JavaScript liest dieselben Daten live.
Aufruf im Repo-Wurzelverzeichnis:
  python3 tools/sections/build_sections.py          # schreibt index.html und en/index.html
  python3 tools/sections/build_sections.py --check  # Exit 1, wenn die Seiten nicht zur Quelle passen
"""
import html, json, re, sys

E = html.escape
STEPS = json.load(open('data/steps.json', encoding='utf-8'))
STATUS = json.load(open('data/status.json', encoding='utf-8'))
FINDINGS = json.load(open('data/findings.json', encoding='utf-8'))
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
        '<section id="nachbauen">',
        '  <div class="wrap">',
        '    <div class="eyebrow">%s</div>' % E(p['eyebrow']),
        '    <h2>%s</h2>' % E(p['h2']),
        '    <p class="intro">%s</p>' % E(p['intro']),
        '    <ol class="steps">',
        *items,
        '    </ol>',
        '    <div class="callout"><p>%s <a href="%s">%s</a></p></div>' % (E(p['callout']), ISSUE, E(p['callout_link'])),
        '    <div class="callout"><p>%s <a href="#umbau">%s</a></p></div>' % (E(p['umbau_text']), E(p['umbau_link'])),
        '  </div>',
        '</section>'])

def history(lang):
    h = STATUS.get('history', [])
    texts = STATUS['en']['history'] if lang == 'en' else [x['text'] for x in h]
    return '\n'.join('          <li><time datetime="%s">%s</time><span>%s</span></li>' % (x['date'], fmt(x['date'], lang), E(t))
                     for x, t in zip(h, texts))

LABELS = {
    'de': {'owner_reported': 'Eigener Bericht', 'in_progress': 'in Arbeit', 'open': 'offen', 'failed': 'Test fehlgeschlagen', 'asof': 'Stand: ', 'last': 'Letzter Test'},
    'en': {'owner_reported': 'Own report', 'in_progress': 'in progress', 'open': 'open', 'failed': 'test failed', 'asof': 'As of ', 'last': 'Latest test'},
}

def texts(lang):
    return STATUS['en'] if lang == 'en' else STATUS

def ms(lang):
    L, T = LABELS[lang], texts(lang)
    names = STATUS['en']['milestones'] if lang == 'en' else {m['id']: m['name'] for m in STATUS['milestones']}
    return '\n'.join('          <li><i class="mk %s"></i><span>%s</span><span class="st">%s</span></li>' % (m['state'], E(names[m['id']]), E(L[m['state']]))
                     for m in STATUS['milestones'])

FIND = {
    'de': {'eyebrow': 'Ehrlich festgehalten', 'h2': 'Befunde und Erkenntnisse',
           'intro': 'Hier stehen Dinge, die schiefgegangen sind oder die wir gelernt haben, neueste zuerst. Offene Sicherheitsdetails nennen wir erst, wenn sie behoben sind; öffentlich steht dann die Lehre daraus.',
           'type': {'finding': 'Erkenntnis', 'problem': 'Problem', 'correction': 'Korrektur'}, 'state': {'open': 'offen', 'resolved': 'geklärt'}},
    'en': {'eyebrow': 'Recorded honestly', 'h2': 'Findings and lessons',
           'intro': 'This is where we record what went wrong or what we learned, newest first. We name open security details only once they are fixed; what we learned is published then.',
           'type': {'finding': 'Finding', 'problem': 'Problem', 'correction': 'Correction'}, 'state': {'open': 'open', 'resolved': 'resolved'}},
}

def findings(lang):
    f = FIND[lang]
    items = []
    for e in FINDINGS['entries']:
        t = e[lang]
        state = '<span class="fstate %s">%s</span>' % (e['state'], E(f['state'][e['state']])) if e.get('state') else ''
        items.append('      <li class="find %s" id="%s"><div class="fhead"><span class="ftype">%s</span>%s<time datetime="%s">%s</time></div><h3>%s</h3><p>%s</p></li>'
                     % (e['type'], e['id'], E(f['type'][e['type']]), state, e['date'], fmt(e['date'], lang), E(t['title']), E(t['text'])))
    return '\n'.join([
        '<section id="befunde">',
        '  <div class="wrap">',
        '    <div class="eyebrow">%s</div>' % E(f['eyebrow']),
        '    <h2>%s</h2>' % E(f['h2']),
        '    <p class="intro">%s</p>' % E(f['intro']),
        '    <ol class="finds">',
        *items,
        '    </ol>',
        '  </div>',
        '</section>'])

def lst(key):
    def f(lang):
        return '\n'.join('          <li>%s</li>' % E(t) for t in texts(lang)[key])
    return f

def binds(s, lang):
    L, T = LABELS[lang], texts(lang)
    ev = T['evidence']
    vals = {'title': T['title'], 'asof': fmt(STATUS['as_of'], lang), 'evidence': ev,
            'meta': L['asof'] + fmt(STATUS['as_of'], lang) + ' \u00b7 ' + ev,
            'lasttest': STATUS['en']['last_test'] if lang == 'en' else STATUS['last_test']['text'],
            'lastdate': L['last'] + ' \u00b7 ' + fmt(STATUS['last_test']['date'], lang)}
    for k, v in vals.items():
        s = re.sub(r'(data-bind="%s">)[^<]*(</)' % k, lambda m: m.group(1) + E(v) + m.group(2), s)
    return s

def jsonld(lang):
    base = 'https://kinetic-it.github.io/lokale-alexa-website/'
    d = {'@context': 'https://schema.org', '@type': 'TechArticle',
         'headline': 'Lokale Alexa: Ein Echo bekommt ein zweites Leben' if lang == 'de' else 'Local Alexa: an Echo gets a second life',
         'inLanguage': lang, 'url': base + ('en/' if lang == 'en' else ''),
         'image': base + 'og-%s.png' % lang,
         'datePublished': '2026-10-25', 'dateModified': STATUS['as_of'],
         'author': {'@type': 'Organization', 'name': 'kinetic-it', 'url': 'https://github.com/kinetic-it'}}
    return '<script type="application/ld+json">%s</script>' % json.dumps(d, ensure_ascii=False)

PARTS = {'jsonld': jsonld, 'nachbauen': steps, 'findings': findings, 'history': history, 'ms': ms, 'confirmed': lst('confirmed'), 'open': lst('not_yet_verified'), 'issues': lst('known_issues')}

def apply(s, lang):
    for key, fn in PARTS.items():
        a, b = '<!-- %s:start -->' % key, '<!-- %s:end -->' % key
        i, j = s.index(a) + len(a), s.index(b)
        s = s[:i] + '\n' + fn(lang) + '\n' + s[j:]
    return binds(s, lang)

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
