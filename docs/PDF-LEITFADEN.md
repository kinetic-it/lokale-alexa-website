# PDF-Leitfaden: Pflege (Stand 26.10.2026)

Zwei PDFs, eine Quelle:

| Datei | Rolle |
|---|---|
| `downloads/Amazon-Geraete-Leitfaden-2026-10-22-neutral.pdf` | deutsches Original, 21 Seiten, **unverändert**, nicht neu bauen |
| `downloads/Amazon-Devices-Guide-2026-10-22-neutral-en.pdf` | englische Fassung, 20 Seiten, gebaut aus `tools/leitfaden/` |

Die englische Fassung ist maschinell übersetzt und von keinem Muttersprachler gelesen. Das steht auf ihrer Titelseite und auf der englischen Webseite.

## Quelle

- `tools/leitfaden/content.de.json`: deutscher Text, aus dem Original-PDF extrahiert (Master).
- `tools/leitfaden/content.en.json`: englischer Text, gleiche Block-IDs und Typen.
- `tools/leitfaden/build_pdf.py`: baut ein PDF aus einer der beiden Dateien (ReportLab, Schrift DejaVu Sans, Paket `fonts-dejavu-core`).
- `tools/leitfaden/logo.jpg`: Logo unten rechts auf jeder Seite (wie im Original).

Gebaut mit `python3 tools/leitfaden/build_pdf.py en downloads/Amazon-Devices-Guide-2026-10-22-neutral-en.pdf`. Ohne Argumente entstehen beide Sprachen unter `tools/leitfaden/build/` (nicht im Git).

Layoutprüfung: Das deutsche PDF, das aus `content.de.json` gebaut wird, hat dieselben 21 Seiten und bis auf einen Zeilenumbruch in einer Tabellenzelle dieselben Zeilenpositionen (Abweichung unter 1 pt) wie das Original.

## Pflege in fünf Schritten

1. Deutsch ändern: nur `content.de.json`.
2. Dieselbe Stelle (gleiche ID) in `content.en.json` übersetzen. Nur Geändertes.
3. `python3 tools/check_i18n.py` muss grün sein (gleiche IDs, Typen, Zahlen, Quellen-IDs, Tabellenform, keine Umlaute im Englischen).
4. PDFs bauen. Bei neuer Fassung Datum in `meta` (Titel, Stand, Fußzeile) und im Dateinamen anpassen.
5. Links in `index.html` und `en/index.html` anpassen.

Hinweis: Das PDF enthält keine Web-Links. Die Quellen Q1 bis Q32 sind nur benannt, ohne URL. Intern gibt es Lesezeichen und ein verlinktes Inhaltsverzeichnis.

## Stand der Prüfung der englischen Fassung

Geprüft: Zahlen (alle Ziffern je Block wie im Deutschen), Quellen-IDs je Block, Fettdruck-Labels, Tabellenform, keine deutschen Reste, Seitenbilder von Titelseite, Inhaltsverzeichnis, Tabellen- und Listenseiten.
Nicht geprüft: Lesung durch einen Muttersprachler, Fachbegriffe gegen die Projektseiten der Quellen.

Die erste englische Fassung (vom 26.10.2026 morgens) hatte Übersetzungsfehler, unter anderem "Measurement measure", "language assistant" statt "voice assistant" und ein falsches deutsches Anführungszeichen. Sie wurde durch diese Fassung ersetzt.
