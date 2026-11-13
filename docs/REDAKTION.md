# Öffentliche Redaktion und Statuspflege

Stand: 13.11.2026 · Work Item: WI-0181

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

- `layouts/partials/sections/<abschnitt>.<sprache>.html`: dauerhafte Erklärungen, Sprachweg-Schaubild, Geräte, Sicherheitsgrundsätze, FAQ und Quellenkontext – Änderungen bewusst von Hand, immer in beiden Sprachen. Die Seite bindet keine externen Schriften, Skripte oder Tracker ein; das soll so bleiben.
- `data/status.json`: freigegebener aktueller Projektstand. Hugo baut ihn in die Seite ein; das JavaScript liest dieselbe Datei beim Aufruf zusätzlich live.
- `downloads/`: freigegebene PDFs / öffentliche Dokumente. Datei muss tatsächlich im Repository liegen und in der Vorlage korrekt verlinkt sein; `tools/check_i18n.py <Ausgabeordner>` meldet Links auf nicht vorhandene Dateien.
- `README.md`: Repo-Zweck und Betrieb.
- `.github/workflows/`: `check.yml` prüft die Quellen, `hugo.yml` baut, prüft die gebaute Seite und veröffentlicht von `main`.

## Sprachen (Deutsch und Englisch)

- Deutsch erscheint unter `/`, Englisch unter `/en/`. Beide Seiten entstehen aus denselben Vorlagen, mit Umschalter DE/EN im Kopf, `hreflang`-Verweisen und eigenem `canonical`.
- Von Hand gepflegter Text liegt je Abschnitt in zwei Dateien: `layouts/partials/sections/<abschnitt>.de.html` und `<abschnitt>.en.html`. Jede inhaltliche Änderung gehört in beide Dateien. Kurze Beschriftungen stehen in `hugo.toml` unter `languages.<sprache>.params`.
- Die dynamischen Statusdaten liegen in `data/status.json`. Deutsche Texte stehen auf oberster Ebene, die englischen im Objekt `en` (mit `milestones` als Zuordnung von ID zu Name). Ohne `en` zeigt die englische Seite den deutschen Text.
- PDF: Deutsch ist der Master (`downloads/Amazon-Geraete-Leitfaden-2026-10-22-neutral.pdf`, unverändert). Die englische Fassung wird aus `tools/leitfaden/` gebaut und ist maschinell übersetzt, ohne Muttersprachler-Prüfung. Pflegeprozess: `docs/PDF-LEITFADEN.md`.
- Vor jedem Merge: `python3 tools/check_i18n.py` (Quellen) und nach einem lokalen Bau `python3 tools/check_i18n.py <Ausgabeordner>` (gebaute Seite). Geprüft werden gleiche IDs, Anker und Tag-Anzahlen in beiden Sprachen, Umlaute im englischen Text, Vollständigkeit der Datendateien, Ziele aller internen Links, Feeds, Sitemap und typische private Angaben (interne IP-Adressen, interne Hostnamen, Work-Item-Nummern). **Nicht** geprüft werden die Qualität der Übersetzung, externe Links und die inhaltliche Richtigkeit. Der Scan auf private Angaben ersetzt die Durchsicht nicht.

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

**Deployment:** Pages-Quelle ist **GitHub Actions**; der Workflow `.github/workflows/hugo.yml` baut mit festgelegter Hugo-Version (Prüfsumme), prüft die gebaute Seite und veröffentlicht von `main`, wenn die Repository-Variable `PAGES_VIA_ACTIONS` auf `true` steht. Am 13.11.2026 geprüft: Die ausgelieferte Seite stammt aus dem Hugo-Bau. Im Hauptordner liegen keine fertigen Seiten mehr; ein Rückfall auf „Deploy from a branch“ ist deshalb nicht mehr möglich. Rückweg bei einem Fehler: den betreffenden Commit zurücknehmen. Offen: Prüfung auf echten Mobilgeräten, in Safari und in Firefox.

## Open Source / Copyright

Eigene Seiteninhalte sind zunächst nur gemäß GitHub-Sichtbarkeit lesbar, **keine** freie Lizenz ist damit automatisch eingeräumt. Die Original-PDF ist mit ausdrücklicher Owner-Freigabe unter `downloads/` öffentlich abgelegt.

## SOUL.md-Beispiel

Abschnitt `#soul` (Navigation „Persona“) und die Downloads `downloads/SOUL-beispiel.md` / `SOUL-example.md` entstehen aus **einer** Quelle: `data/soul.json` (Deutsch und Englisch je Block). Ändern, dann `python3 tools/soul/build_soul.py` (schreibt die beiden Downloads), dann `python3 tools/check_i18n.py`. Den Abschnitt der Seite baut Hugo selbst aus der Quelle. Downloads nicht von Hand ändern.

- Das Beispiel ist erfunden (Figur „Mika“). Nie die echte Persona (Nexis, Speaker) oder Namen, IPs, Schlüssel aus dem Projekt einfügen.
- Aussagen zur Datei (Ablage `~/.hermes/SOUL.md`, Identität am Anfang des Systemprompts, leere Datei = Standard-Identität, Einlesen beim Sitzungsstart, Abgrenzung zu AGENTS.md) stammen aus der Hermes-Dokumentation (Abschnitt Personality). Stand 26.10.2026: nur über eine Suchzusammenfassung gelesen, die Originalseite war aus der Arbeitsumgebung nicht abrufbar, und nicht am eigenen Gerät geprüft. Vor einer Aussage wie „so funktioniert es bei uns“ gegen die Originalseite und die echte Installation prüfen.

## Nachbauen, Verlauf, Testberichte

- Abschnitt `#nachbauen` (sechs Schritte) kommt aus `data/steps.json`, der **Verlauf** im Abschnitt „Stand“ aus `data/status.json` → `history` (mit `en.history`, gleiche Länge). Hugo baut beides beim Veröffentlichen ein; es gibt keinen Zwischenschritt.
- Verlaufseinträge nur mit öffentlich freigegebenen Fakten, ohne interne Namen, Hosts oder Zahlen aus dem privaten Sicherheitsstatus.
- Testberichte: Vorlage `.github/ISSUE_TEMPLATE/testbericht.md` (zweisprachig), verlinkt aus „Nachbauen“ und FAQ.
- `python3 tools/check_i18n.py` prüft, dass alle Datendateien in beiden Sprachen vollständig und gleich aufgebaut sind.

## Stand der Seite aus einer Quelle

`data/status.json` ist die einzige Quelle für den Projektstand. Hugo baut daraus Kopfkarte mit Meilensteinen und letztem Test, die Listen „berichtet / offen / Probleme“, Verlauf, Titel und Datum (auch das Datum im Seitenfuß und im Abschnitt Sprachweg). Das JavaScript liest dieselben Daten live. Meilenstein-Zustände: `owner_reported`, `in_progress`, `open`, `failed`. Neue Felder immer mit englischem Gegenstück unter `en` (`last_test`, `history`, …). Wird der Stand älter als 14 Tage, markiert die Seite das selbst.

Aus derselben Quelle entstehen außerdem:

- **Atom-Feeds** `feed.xml` und `en/feed.xml` aus `history` (neueste zuerst), Vorlage `layouts/index.atom.xml`. Eintrags-IDs bestehen aus Datum und laufender Nummer an diesem Tag; neue Verlaufseinträge deshalb immer hinten anfügen, bestehende nicht umsortieren.
- **JSON-LD** im Seitenkopf (`TechArticle`, `dateModified` = `as_of`), Vorlage `layouts/partials/jsonld.html`.

`check_i18n.py <Ausgabeordner>` prüft Feeds und Sitemap gegen `status.json`.

Abschnittsflächen wechseln per CSS (`main>section:nth-of-type(even)`), keine Klassen von Hand setzen.

Beim Teilen erscheinen `og-de.png` und `og-en.png` (1200 × 630). `sitemap.xml` und `404.html` entstehen aus `layouts/`, `robots.txt` liegt im Hauptordner. GitHub Actions führt `check_i18n.py` bei jedem Pull Request aus (`check.yml` für die Quellen, `hugo.yml` für die gebaute Seite).

## Offen beim Owner (nicht von mir lösbar)

- **Impressum / Kontakt:** Die Seite hat keines. Ob eines nötig ist, hängt von der rechtlichen Einordnung ab (privates, nicht kommerzielles Projekt oder nicht); das entscheidet der Owner. Keine Angaben erfinden.
- **Echtes Foto** des Pilotgeräts (ohne Seriennummer und ohne Umgebung, die etwas verrät) für „Geräte“ oder den Seitenkopf.
- **Muttersprachliche Durchsicht** der englischen Seite und der englischen PDF.
- **Prüfung auf echten Geräten:** Safari (iPhone), Firefox, Android-Chrome. Geprüft ist bisher nur Chromium, mit axe-core (keine Verstöße) und ohne Überlauf bei 320 bis 1440 px.

## Hugo

Die Seite entsteht ausschließlich aus dem Hugo-Projekt; die Umstellung ist seit 13.11.2026 abgeschlossen (alte Seiten im Hauptordner, Python-Generatoren und Vergleichsskript entfernt).

- Das Hugo-Projekt liegt im Hauptordner: `hugo.toml`, `layouts/`, `assets/`, `content/`. Daten in `data/`, Downloads in `downloads/`, Bilder in `images/`. `hugo.toml` bindet sie als `static/` ein, es gibt nur je eine Kopie.
- **Eine Quelle je Inhalt:** `data/status.json`, `data/findings.json`, `data/steps.json`, `data/umbau.json`, `data/soul.json`. Hugo liest sie direkt.
- Hand gepflegter Text steht in `layouts/partials/sections/<abschnitt>.<sprache>.html` (je Abschnitt und Sprache eine Datei). Kopf, Fuß, Kopfzeile und Navigation liegen in `layouts/partials/head|header|footer/<sprache>.html`. CSS und JavaScript stehen einmal in `assets/css/site.css` und `assets/js/site.js`.
- Erzeugte Abschnitte (Nachbauen, Umbau, Befunde, Persona, Stand, Verlauf, Feeds, Sitemap, JSON-LD) sind Vorlagen in `layouts/`.
- **Bau lokal:** `hugo --destination /tmp/out`, danach `python3 tools/check_i18n.py /tmp/out`.
- **Veröffentlichung:** Merge auf `main`; `.github/workflows/hugo.yml` baut, prüft und veröffentlicht.
- Hugo-Version nur bewusst hochziehen (Version und Prüfsumme im Workflow ändern), weil Hugo in fast jedem Release Verhalten ändert. Nach dem Hochziehen die gebaute Seite mit der vorherigen vergleichen.
- Die Downloads `downloads/SOUL-*.md` entstehen mit `python3 tools/soul/build_soul.py`.

## Erfahrungsbericht „So haben wir unseren Echo 2 umgebaut“

Abschnitt `#umbau` (Navigation „Umbau“ / „Our build“) entsteht aus **einer** Quelle: `data/umbau.json` (Deutsch und Englisch je Etappe, gleiche Struktur). Ändern, dann `python3 tools/check_i18n.py`. Hugo baut den Abschnitt beim Veröffentlichen aus der Quelle (`layouts/partials/sections/umbau.html`).

- Jede Etappe hat feste Felder: Voraussetzungen, was wir gemacht haben, mögliche Schwierigkeiten, persönlicher Aufwand, Nachweis des Erfolgs, Quellen. Jede Etappe trägt Kennzeichen: Getestet (Owner-Beobachtung), Berichtet, In Entwicklung, Geplant, Angabe eines Fremdprojekts, Nicht belegt.
- **Stimme:** Ich-Form, so als würde der Owner selbst schreiben. In öffentlichen Texten kein „Owner“ in der dritten Person und kein Aktenton wie „nicht festgehalten“; Evidenz als „Selbst getestet“ oder „Eigener Bericht“ kennzeichnen. Fremdangaben klar als solche benennen, aber freundlich und knapp, ohne wiederholte Warnsprüche (die große Warnung steht einmal oben und kurz vor den riskanten Etappen).
- **Aufwandsbewertung (1 bis 5) und Zeiten stammen vom Owner** (Interview 30.10.2026) und nie von einer KI. Fehlt eine Angabe, steht „nicht bewertet“. Nichts schätzen oder auffüllen.
- Keine Befehle, Schritte oder Versionsnummern ohne Beleg. Was ein Fremdprojekt vorgibt, steht als Fremdangabe da; für die einzelnen Schritte auf die Originalanleitung verlinken statt sie abzuschreiben. Keine eigene Pad-Belegung veröffentlichen, solange sie nicht durchgemessen ist.
- Die Warnung „OHNE GEWÄHR – AUF EIGENE GEFAHR“ (englisch „NO WARRANTY – AT YOUR OWN RISK“) steht groß vor der Anleitung und als Kurzhinweis vor Etappen mit Hardware-, Unlock- oder Flash-Eingriff (`"warn": true`). Sie ist ein deutlicher Hinweis und keine rechtliche Pauschalfreistellung.
- Fremde 3D-Dateien und Software nur verlinken, nicht in dieses Repository kopieren (Lizenzen nicht geprüft).
- **Fotos** liegen in `images/`, nur mit ausdrücklicher Freigabe des Owners. Vor dem Ablegen: Metadaten entfernen (EXIF, GPS, Aufnahmedatum), Seriennummern, Aufkleber, MAC-Adressen und private Umgebung wegschneiden, auf höchstens 700 px Breite verkleinern. Jedes Bild braucht einen Alternativtext in beiden Sprachen.
- Zahlen zum Kinetic Voice Router stammen aus Owner-Beobachtungen. Eine Version gilt erst als installiert oder abgenommen, wenn der Owner das gemeldet hat. Der eigenständige Kinetic Voice Router wird inzwischen öffentlich unter `https://github.com/kinetic-it/kinetic-voice-router` entwickelt; historische Berichtsstände im Umbau-Abschnitt sind auf ihren jeweiligen Berichtstag zu beziehen.

## Befunde und Erkenntnisse

Abschnitt `#befunde` kommt aus `data/findings.json` (je Eintrag Deutsch und Englisch, neueste zuerst). Neuer Eintrag: Objekt oben einfügen, `python3 tools/check_i18n.py`, PR. Typen: `finding` (Erkenntnis), `problem` (mit Zustand `open` oder `resolved`), `correction` (Korrektur einer früheren öffentlichen Aussage).

**Veröffentlichungsregel (Owner-Freigabe 26.10.2026):**

- **Sofort veröffentlichen:** fehlgeschlagene Tests, falsche frühere öffentliche Aussagen (als Korrektur), Grenzen von Geräten und Software, Erkenntnisse, die Leser vor einem Fehler bewahren.
- **Erst nach der Behebung:** offene Sicherheitsdetails, zum Beispiel unsaubere Freigaben. Öffentlich steht dann nur die Lehre daraus, ohne Gerätenamen und ohne Angriffsweg.
- **Nie:** Namen, Hosts, IPs, Zugangsdaten, Geräte oder Gewohnheiten aus dem Haushalt.
- Ein Problem bleibt `open`, bis die Ursache belegt behoben ist. Beim Schließen den Eintrag auf `resolved` setzen und den Text anpassen; nichts still löschen.

Die zugehörige Auslöser-Regel (nach jedem Test oder Befund über die Veröffentlichung entscheiden) steht im privaten Repository `lokale_alexa`.

