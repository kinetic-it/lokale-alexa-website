#!/usr/bin/env python3
"""Erzeugt aus data/soul.json die Downloads downloads/SOUL-beispiel.md und downloads/SOUL-example.md.
Der Abschnitt "Persona" der Seite entsteht direkt in Hugo (layouts/partials/sections/soul.html) aus derselben Quelle.
Aufruf im Repo-Wurzelverzeichnis:
  python3 tools/soul/build_soul.py          # schreibt
  python3 tools/soul/build_soul.py --check  # Exit 1, wenn die Downloads nicht zur Quelle passen
"""
import json, sys

C = json.load(open('data/soul.json', encoding='utf-8'))

def md(lang):
    parts = ['\n'.join(b[lang]['lines']) for b in C['blocks']]
    return '\n\n'.join(parts) + '\n'

def main():
    check = '--check' in sys.argv
    ok = True
    for lang in ('de', 'en'):
        f = 'downloads/' + C['file_names'][lang]
        if check:
            try: ok &= open(f, encoding='utf-8').read() == md(lang)
            except FileNotFoundError: ok = False
        else: open(f, 'w', encoding='utf-8').write(md(lang))
    if check and not ok:
        print('soul: Downloads passen nicht zu data/soul.json (python3 tools/soul/build_soul.py)'); sys.exit(1)
    print('soul: OK' if check else 'soul: geschrieben')

main()
