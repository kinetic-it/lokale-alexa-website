# Lokale Alexa – öffentliche Projektwebsite

Öffentliche Projektinformationen zu einem wiederverwendeten Amazon Echo als Home-Assistant-Sprachsatellit mit optionalem Hermes-Speaker.

- Projektüberblick, Gerätekompatibilität, Softwarewege, FAQ und Sicherheitsgrenzen: [Website](https://kinetic-it.github.io/lokale-alexa-website/) (GitHub Pages aktiv seit 25.10.2026)
- **Öffentlich:** nur geprüfte, ausdrücklich freigegebene Aussagen.
- **Privat:** technische Projektakte, Work Items, Konfigurationen und interne Evidenz verbleiben in `kinetic-it/lokale_alexa` und `kinetic-it/work-items`.

## Aktualisierung

`data/status.json` ist der **freigegebene** öffentliche Status. Inhalte und FAQ werden manuell gepflegt, Statusänderungen nach einem Review übernommen. GitHub Pages veröffentlicht Änderungen auf `main` automatisch (Branch `main`, Ordner `/ (root)`). Es existiert **kein** automatischer Direktzugriff auf das private Repository.

Die Seite zeigt Sprachweg-Schaubild, Gerätefilter, Sicherheitsgrundsätze und den freigegebenen Pilotstand (aus `data/status.json`). Sie lädt keine externen Ressourcen. Es gibt eine deutsche und eine englische Fassung (`en/`), siehe `docs/REDAKTION.md`.

Die Grundlagen stammen aus „Amazon-Geräte als offene Sprach- und Smart-Home-Geräte“ (Redaktionsstand 22.10.2026). Geräteunterstützung und tatsächliche Projektabnahme werden getrennt dargestellt.

Work Item (privat): WI-0181.

## PDF-Leitfaden

Deutsches Original und englische Fassung: `downloads/`. Die englische PDF wird aus `tools/leitfaden/` gebaut; Pflegeprozess in `docs/PDF-LEITFADEN.md`.

## Hugo

Die Seite wird mit [Hugo](https://gohugo.io/) gebaut (Umstellung läuft, siehe `docs/REDAKTION.md`, Abschnitt „Hugo“). Lokal: `hugo --destination /tmp/out` und `python3 tools/hugo_parity.py /tmp/out`.
