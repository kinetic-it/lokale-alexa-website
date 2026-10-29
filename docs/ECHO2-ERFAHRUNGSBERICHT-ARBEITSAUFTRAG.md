# WI-0181 – Website-Erfahrungsbericht und Nachbau-Anleitung (Redaktionsauftrag)

**Stand der Vorbereitung:** 30.10.2026 · **Auftrag:** [Website-Issue #21](https://github.com/kinetic-it/lokale-alexa-website/issues/21) · **Status:** Interview und Ausarbeitung offen; **nicht veröffentlichen / nicht mergen**.

## Ausgangspunkt

Diese Datei ist der Arbeitsauftrag für die Website-Redaktion, **noch keine veröffentlichte Bauanleitung**.

Bereits belegter Ausgangspunkt: Echo 2 (Modell XC56PY, Codename radar) wurde über die Bodenkontakte mit einem gedruckten Pogo-Halter in Fastboot erreicht; Unlock und TWRP wurden vom Owner mit konkreten Rückmeldungen nachgewiesen. Später liefen echo-dot-assist, lokales Wakeword „Okay Nabu“ und der Home-Assistant-/Hermes-Sprachweg in einzelnen Tests. Aussagen zu „vollständig lötfrei“, genau benutzter STL/ZIP, benötigten Minuten, Werkzeug, Schwierigkeit, Dauerstabilität und verifiziertem vollständigem Rohbackup **sind nicht belegt** und müssen vor einer Veröffentlichung erfragt oder offengelassen werden.

**Technische Aktualität (nur Orientierungsstand):** Stand 29./30.10.2026: Die Home-Assistant-Custom-Integration Kinetic Voice Router 0.4.1 wurde live in Beobachten und Aktiv getestet, einschließlich lokaler Statusabfrage und Hermes-Wissensfrage. Bei einer unbekannten Statusfrage gab es eine Fehlklassifikation und eine erfundene Hermes-Zustandsbehauptung. R3.2/0.4.2 liegt als Entwickler-/Teststand vor, ist nicht als am Echo/HA installiert bestätigt. Keine vollständige Alltags- oder Sicherheitsabnahme behaupten.

## Veröffentlichungs-Gate und Quellen

Die kanonische Redaktionsanleitung bleibt [REDAKTION.md](REDAKTION.md). Der tatsächliche veröffentlichte Status liegt in [data/status.json](../data/status.json), Erkenntnisse in [data/findings.json](../data/findings.json). Das öffentlich sichtbare „Nachbauen“ entsteht aus [tools/sections/steps.json](../tools/sections/steps.json). Redaktions-KI gleicht erst die berechtigte private Fachakte ab, führt das Owner-Interview, stellt Belege zusammen und erstellt **einen Draft-PR**; nach Review erst durch Owner-Entscheidung veröffentlichen.

Nie mit Telefonnummern, Netzadressen, Zugangsdaten, Seriennummern, Audio-Rohmaterial, privaten Nutzer-/Familiennamen, internen HA-Entity-IDs, privaten Logs oder Sicherheitsdetails auffüllen. 3D-Druckdateien fremder Projekte verlinken, nicht ohne Rechte in dieses Repository kopieren.

## Geplanter Website-Abschnitt – „So haben wir den Echo 2 umgebaut“

Ergänzend zum vorhandenen allgemeinen Sechs-Schritte-Abschnitt, nicht als Ersatz:

1. **Gerät und Grenzen:** Echo 2 XC56PY/radar identifizieren, exakte Revision/Firmware und Projektkompatibilität; andere Echo-/Dot-/Show-Varianten separat behandeln.
2. **Warum ein Pogo-Adapter?** 3D-gedruckter Kontakt-Halter für den Bodenschacht statt direktem Löten als Owner-Präferenz; dokumentieren, ob tatsächlich vollständig ohne Löten gearbeitet wurde und ob der benutzte Halter dem verlinkten LibreEcho-V5-Modell entspricht.
3. **Vorbereitung:** passende Originalprojektanleitungen, datensparsame Checkliste zu Werkzeug, Download-/Lizenz- und Versionsprüfung, Backup-/Recovery-Grenzen.
4. **Zugang zum Gerät:** allgemein nachvollziehbarer Ablauf zur Kontaktierung, USB/Fastboot, Unlock und Recovery, **nur** anhand überprüfter originaler Geräteanleitungen und belegter Owner-Schritte; riskante Befehle und Voraussetzungen besonders deutlich markieren. Keine universalisierten Pinouts oder Fremdmodelle.
5. **Software-Entscheidung:** verschiedene Wege differenzieren (Fire-OS-basierter Assist-Weg vs. Ersatz-Firmware); für die eigene Umsetzung tatsächliche Softwareversion und Grund für die Wahl dokumentieren.
6. **Home Assistant und Hermes:** Assist-Pipeline, lokales Wakeword, nachgewiesene Status-/Geräte- und Wissensfragen; korrekte Trennung zwischen lokaler Intent-Verarbeitung und Hermes-Fallback.
7. **Tatsächlich erreichte Ergebnisse, Probleme, offene Tests:** Was funktioniert? Was war schwer? Was dauerte länger? Was ist nur geplant?
8. **Aufwand:** Owner-eigene Bewertung je Etappe **1–5**, Zeit nur wenn berichtet, nötige Vorkenntnisse, mögliche Folgekosten; keine von der KI erfundene „Erfolgsquote“.

Direkt **vor** jeder technischen Anleitung als deutliche, kontrastreiche Überschrift im Seiteninhalt:

> **OHNE GEWÄHR – AUF EIGENE GEFAHR**
>
> Entsperren, Firmware-/Recovery-Schreibzugriffe und fehlerhafte elektrische Kontaktierung können Geräte dauerhaft beschädigen und Daten oder Funktionen zerstören. Der Bericht gilt ausschließlich für die konkret geprüfte Geräte-/Softwarekombination. Er ersetzt nicht die Originalanleitungen. Es gibt **keine Garantie**, dass die Schritte mit anderen Geräten oder Versionen funktionieren.

Englisch sinngemäß in `en/index.html`:

> **NO WARRANTY – AT YOUR OWN RISK**

Dies ist ein deutlich sichtbarer Warnhinweis, aber keine Aussage, dass jede gesetzliche Haftung ausgeschlossen sei.

## Interview – kurze Einzelfragen, keine Vermutungen

**Erst nach Sichtung der belegten Fakten fragen.** Immer genau **eine** konkrete Frage pro Chat-Nachricht, Antworten durch den Owner prüfen lassen und auf dessen ADHS-freundliche Arbeitsweise achten. Fragen können nacheinander folgende **noch offene** Aspekte erfassen:

- War der tatsächlich eingesetzte gedruckte Pogo-Halter **LibreEcho Echo Gen2 V5** oder ein anderes Modell? Wurde er selbst gedruckt oder bezogen?
- Hast du bei deinem Aufbau tatsächlich komplett auf **Löten** verzichtet oder wurden einzelne Kabel/Kontakte trotzdem gelötet?
- Wie aufwendig war Drucken/Anpassen/Positionieren des Adapters? Welches Material/Werkzeug hat funktioniert?
- Was war beim USB-Kontakt/Fastboot zunächst schwierig? Was hat schließlich geholfen?
- Wie schwierig waren Unlock/TWRP und die Softwareinstallation; wie viel Zeit ungefähr?
- Was war bei Wakeword, Mikrofon/Lautsprecher, Home Assistant und Hermes leicht bzw. schwer?
- Welche Fehlversuche/Überraschungen möchtest du anderen ersparen? Welche Dinge würdest du nächstes Mal anders machen?
- Wie beurteilst du die Phasen persönlich von 1 (sehr leicht) bis 5 (sehr schwer)?
- Welche Fotos, 3D-Dateien oder Links darf die Website veröffentlichen? Drittanbieter-Lizenzen vorher prüfen.
- Welche Funktionen sind wirklich alltäglich zuverlässig, welche sind nur Einzeltests oder noch geplant?

**Keine selbst erfundenen Besitzer-Antworten.** Nach dem Interview alle Aussagen in einer kurzen Owner-Freigabefassung zusammenfassen, ausdrücklich Bestätigung erbitten.

## Umsetzungskriterien

- Inhaltstrennung: **Owner-Erfahrung / im Projekt nachgewiesen / Aussage eines Fremdprojekts / Plan / ungeprüft**.
- Hardware- und Root-Wege nur modellgebunden. Offene Risiken/Backups/Fehlschläge nicht verschweigen.
- Nutzerfreundlich auf Mobilgeräten, mit wenigen aufeinander aufbauenden Schritten, Inhaltsverzeichnis und Download-Links zu den **Original**-3D-Dateien.
- Deutsch und Englisch gleicher Informationsstand, keine ungeprüften Privatdaten.
- Bestehende Quellen **generatorbasiert** pflegen; `python3 tools/sections/build_sections.py`, `python3 tools/feed/build_feed.py`, `python3 tools/check_i18n.py`; Build und GitHub CI prüfen.
- **Kein Merge und kein GitHub-Pages-Publish vor Owner-Abnahme.**

## Öffentliche Recherchequellen

- [LibreEcho – Echo-2-Installationsweg](https://github.com/aslater3/LibreEcho/blob/main/docs/install/README.md)
- [LibreEcho – Echo Gen2 Pogo-Plug V5 (3D-Druck-Archiv)](https://github.com/aslater3/LibreEcho/raw/refs/heads/main/tools/libreecho-echo-gen2-pogo-plug-v5.zip)
- [echo-dot-assist – Upstream-Projekt](https://github.com/Gamer92000/echo-dot-assist)
- [Öffentlicher Amazon-Geräte-Leitfaden als PDF](../downloads/Amazon-Geraete-Leitfaden-2026-10-22-neutral.pdf)

**Nächste Aktion für die Website-KI:** Den aktuellen Repo- und Belegstand prüfen und die **erste** noch ungeklärte Frage zum tatsächlich verwendeten 3D-Druckhalter stellen. Bis dahin kann die Struktur vorbereitet, aber nicht als Erfahrungsbericht veröffentlicht werden.
