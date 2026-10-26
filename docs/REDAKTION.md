# Öffentliche Redaktion und Statuspflege

Stand: 25.10.2026 · Work Item: WI-0181

## Zwei getrennte Repositories

- **Privat:** `kinetic-it/lokale_alexa` – technischer Ist-Stand, Entscheidungen, Tests und fachliche Dokumentation. Das kanonische WI liegt gesondert privat unter `kinetic-it/work-items`.
- **Öffentlich:** `kinetic-it/lokale-alexa-website` – journalistisch lesbare Erklärungen, hardwarebezogene Recherche und ein **explizit freigegebener** öffentlicher Status.

Öffentliche Seiten dürfen weder interne Work-Item-Verläufe noch private Endpunkte, Benutzerdaten, Tokens, Netzwerkpfade, Rohlogs, Transkripte oder Geräteseriennummern enthalten.

## Status aktualisieren

1. Im privaten Repo `STATE.md`, Abnahmen und das zentrale WI anhand neuer Evidenz aktualisieren.
2. Änderungen fachlich einordnen: direkt getestet / Owner-Bericht / Fremdprojekt-Aussage / Plan / ungeprüft.
3. Nur geeignete Aussagen **manuell redaktionell freigeben** und `data/status.json` ändern. `approved: true` ist eine deklarierte redaktionelle Freigabe, keine technische Sicherheitsprüfung.
4. Pull Request prüfen: keine Secrets, keine privaten URLs, keine falschen PASS-Behauptungen, Quellen-/Modellnummern korrekt.
5. Merge nach `main`; GitHub Pages veröffentlicht die neue Seite automatisch. Das ist Veröffentlichung eines bereits geprüften Standes, kein Live-Sync aus Home Assistant.

Ein vollautomatischer, unbeaufsichtigter Export aus dem privaten Repo ist **nicht eingerichtet**. Für einen späteren automatischen Export wären ein minimaler öffentlicher Datensatz, ein begrenzter Lesekanal, ein menschliches Freigabegate, ein Validierer und eine sichere Deployment-Kette nötig. Ein Job mit privatem Repo-Token im öffentlichen Repo ist ausgeschlossen.

## Redaktioneller Umfang

- `index.html`: dauerhafte Erklärungen, Sprachweg-Schaubild, Geräte, Sicherheitsgrundsätze, FAQ und Quellenkontext – Änderungen bewusst von Hand. Die Seite bindet keine externen Schriften, Skripte oder Tracker ein; das soll so bleiben.
- `data/status.json`: freigegebener aktueller Projektstand; die Website lädt diesen beim Aufruf.
- `downloads/`: freigegebene PDFs / öffentliche Dokumente. Datei muss separat tatsächlich hochgeladen und im HTML korrekt verlinkt werden.
- `README.md`: Repo-Zweck und Betrieb.
- `.github/workflows/`: optional späterer automatischer Validierungs-/Build-Prozess. GitHub Pages kann die Root-Dateien auch ohne Build auf `main` bereitstellen.

## Sprachen (Deutsch und Englisch)

- Deutsch: `index.html`, Englisch: `en/index.html`. Beide sind eigenständige statische Seiten mit Umschalter DE/EN im Kopf, `hreflang`-Verweisen und eigenem `canonical`.
- Die Seiten werden **beide von Hand gepflegt**. Jede inhaltliche Änderung gehört in beide Dateien.
- Die dynamischen Statusdaten liegen in `data/status.json`. Deutsche Texte stehen auf oberster Ebene, die englischen im Objekt `en` (mit `milestones` als Zuordnung von ID zu Name). Ohne `en` zeigt die englische Seite den deutschen Text.
- Beide PDF-Sprachen werden aus einer einzigen Layout-Implementierung in `tools/leitfaden/build_pdf.py` erzeugt. Die veröffentlichte deutsche Original-PDF vom 22.10.2026 bleibt unverändert.
- Deutsch ist der Master. Änderungen **nur** in `tools/leitfaden/content.de.json` vornehmen.
- Für neue oder geänderte Absätze nur die betroffenen IDs in `content.en.json` übersetzen; beide Sprachen behalten dieselben IDs.
- `python3 tools/leitfaden/build_pdf.py` erzeugt das neue englische PDF unter `downloads/` und den deutschen Vergleich im `scratchpad/`.
- `python3 tools/check_i18n.py` prüft gleiche IDs und Website-Struktur.
- Bei einer neuen Ausgabe Datum im PDF, Dateinamen und „Stand“ erhöhen, Downloadlinks aktualisieren und die englische Version vor Veröffentlichung ausdrücklich vom Owner freigeben lassen.
- Vor jedem Merge: `python3 tools/check_i18n.py`. Das Skript prüft gleiche IDs (Website und PDF-Quelltexte), Anker, Tag-Anzahlen, Umlaute im englischen Webtext und die Vollständigkeit von `status.json`. Es prüft **nicht** die Qualität der Übersetzung.

## Vor jedem Merge prüfen

- **Schaubild und Texte sind öffentlich bereinigt.** Keine Ports, VM- oder Hostnamen, IP-Adressen, Entity-Namen, Zahlen zu Freigaben, Modell- oder Anbieternamen interner Dienste, keine ungeschlossenen Schwachstellen. Sicherheitsaussagen nur als Grundsatz oder Ziel formulieren, nie als Zusicherung. Quelle ist der freigegebene Stand, nicht die private `SICHERHEIT.md`.
- Kein Zugriff des Website-Codes auf private GitHub-Repos; keine Geheimnisse im JS/HTML/JSON.
- `data/status.json` valide und explizit freigegeben; Version und Datum aktualisiert; englisches Objekt `en` mitgepflegt.
- Jede Gerätebehauptung trennt Unlock, historischen Root, experimentellen Port und funktionierenden Sprachsatelliten.
- Aushänge zum aktuellen Pilotstatus entsprechen den zuletzt geprüften privaten Canonicals.
- PDF-Download nur als verfügbar bezeichnen, wenn Binärdatei im öffentlichen Git vorhanden und abrufbar ist.
- Test: Startseite auf Desktop/Mobilgerät, Navigation, Statusabruf, 404-Links und GitHub-Pages-Deployment.

## Deployment

**Ziel:** `https://kinetic-it.github.io/lokale-alexa-website/`.

GitHub → Repository → Settings → Pages → **Deploy from a branch**, Branch `main`, Ordner `/ (root)`. Seit 25.10.2026 aktiv; Website, `data/status.json` und PDF waren live erreichbar. Offen: vollständige Mobilansicht und Test aller Navigationspunkte.

## Open Source / Copyright

Eigene Seiteninhalte sind zunächst nur gemäß GitHub-Sichtbarkeit lesbar, **keine** freie Lizenz ist damit automatisch eingeräumt. Die Original-PDF ist mit ausdrücklicher Owner-Freigabe unter `downloads/` öffentlich abgelegt.
