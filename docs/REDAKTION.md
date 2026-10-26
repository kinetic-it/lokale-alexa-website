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
- PDF: Deutsch ist der Master (`downloads/Amazon-Geraete-Leitfaden-2026-10-22-neutral.pdf`, unverändert). Die englische Fassung wird aus `tools/leitfaden/` gebaut und ist maschinell übersetzt, ohne Muttersprachler-Prüfung. Pflegeprozess: `docs/PDF-LEITFADEN.md`.
- Vor jedem Merge: `python3 tools/check_i18n.py`. Das Skript prüft gleiche IDs, Anker, Tag-Anzahlen, Umlaute im englischen Text und die Vollständigkeit von `status.json`. Es prüft **nicht** die Qualität der Übersetzung.

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

## SOUL.md-Beispiel

Abschnitt `#soul` (Navigation „Persona“) und die Downloads `downloads/SOUL-beispiel.md` / `SOUL-example.md` entstehen aus **einer** Quelle: `tools/soul/content.json` (Deutsch und Englisch je Block). Ändern, dann `python3 tools/soul/build_soul.py`, dann `python3 tools/check_i18n.py`. Seiten und Downloads nicht von Hand ändern.

- Das Beispiel ist erfunden (Figur „Mika“). Nie die echte Persona (Nexis, Speaker) oder Namen, IPs, Schlüssel aus dem Projekt einfügen.
- Aussagen zur Datei (Ablage `~/.hermes/SOUL.md`, Identität am Anfang des Systemprompts, leere Datei = Standard-Identität, Einlesen beim Sitzungsstart, Abgrenzung zu AGENTS.md) stammen aus der Hermes-Dokumentation (Abschnitt Personality). Stand 26.10.2026: nur über eine Suchzusammenfassung gelesen, die Originalseite war aus der Arbeitsumgebung nicht abrufbar, und nicht am eigenen Gerät geprüft. Vor einer Aussage wie „so funktioniert es bei uns“ gegen die Originalseite und die echte Installation prüfen.

## Nachbauen, Verlauf, Testberichte

- Abschnitt `#nachbauen` (sechs Schritte) kommt aus `tools/sections/steps.json`, der **Verlauf** im Abschnitt „Stand“ aus `data/status.json` → `history` (mit `en.history`, gleiche Länge). Danach `python3 tools/sections/build_sections.py` (schreibt den statischen Fallback in beide Seiten; das JavaScript liest `history` zusätzlich live aus `status.json`).
- Verlaufseinträge nur mit öffentlich freigegebenen Fakten, ohne interne Namen, Hosts oder Zahlen aus dem privaten Sicherheitsstatus.
- Testberichte: Vorlage `.github/ISSUE_TEMPLATE/testbericht.md` (zweisprachig), verlinkt aus „Nachbauen“ und FAQ.
- `python3 tools/check_i18n.py` prüft alle generierten Teile gegen ihre Quellen.

## Stand der Seite aus einer Quelle

`data/status.json` ist die einzige Quelle für den Projektstand. `python3 tools/sections/build_sections.py` schreibt daraus den statischen Fallback in beide Seiten (Kopfkarte mit Meilensteinen und letztem Test, Listen „berichtet / offen / Probleme“, Verlauf, Titel, Datum). Das JavaScript liest dieselben Daten live. Meilenstein-Zustände: `owner_reported`, `in_progress`, `open`, `failed`. Neue Felder immer mit englischem Gegenstück unter `en` (`last_test`, `history`, …). Wird der Stand älter als 14 Tage, markiert die Seite das selbst.

Abschnittsflächen wechseln per CSS (`main>section:nth-of-type(even)`), keine Klassen von Hand setzen.

Beim Teilen erscheinen `og-de.png` und `og-en.png` (1200 × 630). `robots.txt`, `sitemap.xml` und `404.html` liegen im Wurzelverzeichnis. Eine GitHub Action (`.github/workflows/check.yml`) führt `check_i18n.py` bei jedem Pull Request aus.

## Offen beim Owner (nicht von mir lösbar)

- **Impressum / Kontakt:** Die Seite hat keines. Ob eines nötig ist, hängt von der rechtlichen Einordnung ab (privates, nicht kommerzielles Projekt oder nicht); das entscheidet der Owner. Keine Angaben erfinden.
- **Echtes Foto** des Pilotgeräts (ohne Seriennummer und ohne Umgebung, die etwas verrät) für „Geräte“ oder den Seitenkopf.
- **Muttersprachliche Durchsicht** der englischen Seite und der englischen PDF.
- **Prüfung auf echten Geräten:** Safari (iPhone), Firefox, Android-Chrome. Geprüft ist bisher nur Chromium, mit axe-core (keine Verstöße) und ohne Überlauf bei 320 bis 1440 px.

