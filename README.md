# Lokale Alexa – öffentliche Projektwebsite

Öffentliche Projektinformationen zu einem wiederverwendeten Amazon Echo als Home-Assistant-Sprachsatellit mit optionalem Hermes-Speaker.

- Website: https://kinetic-it.github.io/lokale-alexa-website/ (Deutsch) und `/en/` (Englisch)
- **Öffentlich:** nur geprüfte, ausdrücklich freigegebene Aussagen.
- **Privat:** technische Projektakte, Work Items, Konfigurationen und interne Evidenz verbleiben in `kinetic-it/lokale_alexa` und `kinetic-it/work-items`. Es gibt keinen automatischen Zugriff auf private Repositories.

Work Item (privat): WI-0181.

## Aufbau

Die Seite wird ausschließlich mit [Hugo](https://gohugo.io/) gebaut. Im Hauptordner liegen keine fertigen Seiten.

| Pfad | Inhalt |
|---|---|
| `data/status.json` | freigegebener öffentlicher Projektstand, Meilensteine, Verlauf (Deutsch und Englisch) |
| `data/findings.json` | Befunde und Erkenntnisse |
| `data/steps.json`, `data/umbau.json`, `data/soul.json` | Abschnitte Nachbauen, Umbau, Persona |
| `layouts/partials/sections/*.de.html` / `*.en.html` | von Hand gepflegte Texte je Abschnitt und Sprache |
| `layouts/` (übrige Dateien) | Vorlagen für Seite, Feeds, Sitemap, 404 |
| `assets/` | CSS und JavaScript (einmal, für beide Sprachen) |
| `downloads/`, `images/` | PDFs, SOUL-Beispiel, Fotos |
| `tools/check_i18n.py` | Prüfung der Quellen und der gebauten Seite |
| `tools/leitfaden/`, `tools/soul/` | bauen die englische PDF und die SOUL-Downloads |

## Stand aktualisieren

1. `data/status.json` (und bei Bedarf `data/findings.json`) ändern, immer Deutsch und Englisch.
2. Betrifft die Änderung auch Fließtext (zum Beispiel FAQ oder Sprachweg), die passenden Dateien unter `layouts/partials/sections/` in beiden Sprachen anpassen.
3. Pull Request öffnen. Die Prüfungen laufen automatisch.
4. Nach Durchsicht und Merge auf `main` baut und veröffentlicht GitHub Actions die Seite.

Regeln für Inhalte, Freigabe und Sprache: `docs/REDAKTION.md`. PDF-Leitfaden: `docs/PDF-LEITFADEN.md`.

## Lokal bauen und prüfen

Hugo-Version wie in `.github/workflows/hugo.yml` festgelegt.

```bash
hugo --destination /tmp/out
```

```bash
python3 tools/check_i18n.py /tmp/out
```

Ohne Ordnerangabe prüft `tools/check_i18n.py` nur die Quellen.

## Veröffentlichung

`.github/workflows/hugo.yml` baut bei jedem Pull Request und jedem Push auf `main`, prüft die gebaute Seite und veröffentlicht von `main` aus über GitHub Pages (Quelle „GitHub Actions“, Repository-Variable `PAGES_VIA_ACTIONS=true`). Ein Zurückschalten auf „Deploy from a branch“ ist nicht mehr möglich, weil der Hauptordner keine fertige Seite enthält. Rückweg bei einem Fehler: den betreffenden Commit zurücknehmen.

Die Seite lädt keine externen Schriften, Skripte oder Tracker.
