# Cashflow Guardian

Lokale Rechnungsauswertung mit zwölf Oberflächensprachen, eingebetteten Flaggen,
Diagrammen und kombinierbaren Filtern. Aktueller Stand: **v0.7**, einschließlich
Rechnungsdatum und sprachabhängiger Datumsanzeige.

## Offline ausprobieren

Repository herunterladen und `Cashflow_Guardian_v0.7.html` im Browser öffnen.
`Cashflow_Guardian_Demo.html` ist dieselbe aktuelle Demo. Keine Installation,
Zugangsdaten oder externen Dienste erforderlich. Alle enthaltenen Rechnungen sind erfunden.

## Funktionen

- Gruppen nach Kunde, Zahlungsstatus, Fälligkeitsmonat oder Prüfpriorität.
- Monatsbalken, Gruppenwahl, Suche und Währung gemeinsam als Filter.
- Getrennte offene und bezahlte Beträge; Teilzahlungen werden aufgeteilt.
- Sortierbare Rechnungsliste mit Rechnungsdatum und Fälligkeit.
- CSV-Export der gefilterten Auswahl.
- Deutsch, English, Español, Français, Português (Portugal), Italiano, 中文,
  हिन्दी, 日本語, Polski, Română und Nederlands.
- Gespeicherte Sprachwahl, lokalisierte Datums-/Zahlenformate und stabile Seitenanordnung.
- Lokale Hinweise auf ähnliche Rechnungen und ungewöhnliche Beträge mittels TF-IDF
  und IsolationForest; Hinweise müssen manuell geprüft werden.

Die Monatsübersicht zeigt Fälligkeiten, keine tatsächlichen Zahlungseingänge.
Währungen werden nicht zusammengerechnet. Die Offline-Demo enthält einen festen
Beispieldatenstand; die Server-Demo erzeugt Datumswerte relativ zum aktuellen Tag.

## Lokaler Server

Python 3.11 oder neuer:

```console
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python server.py
```

Die angezeigte Adresse im Browser öffnen. Der Server bindet an localhost.
Standardmäßig werden ausschließlich Beispieldaten verwendet.

Optional liest der Server PayPal-Sandbox-Rechnungen. Zugangsdaten ausschließlich
lokal über die Umgebungsvariablen `PAYPAL_SANDBOX_CLIENT_ID` und
`PAYPAL_SANDBOX_CLIENT_SECRET` bereitstellen. Keine Zugangsdaten in den Quellcode,
in GitHub oder in HTML-Dateien schreiben. Die Anwendung lädt keine `.env`-Dateien
automatisch. Produktionskonten und schreibende Zahlungsvorgänge werden nicht verwendet.

## Weiterentwicklung und Tests

`static/index.html`, `static/style.css`, `static/i18n.js` und `static/app.js`
sind die gemeinsame Oberfläche für Server und Offline-Demo.

```console
python build_offline.py
python -m pytest -q
```

Der Offline-Build übernimmt nur die enthaltenen synthetischen Daten aus der
unverändert aufbewahrten v0.6-HTML-Datei. Er ist unabhängig von Sandbox-Zugangsdaten.
Nach Änderungen an `static/` beide generierten aktuellen HTML-Dateien mit einchecken.
Flaggen sind in `i18n.js` eingebettet und zusätzlich unter `assets/flags/` verfügbar.

Änderungen auf einem neuen Branch durchführen, Tests ausführen und per Pull Request
gegen `main` einreichen. Lokale Bankexporte, CSVs, Umgebungsdateien und Backups
gehören nicht ins Repository. GitHub Actions führt die Python-Tests und einen
Abgleich der generierten Demo aus.

Die lokale Veröffentlichung wurde zusätzlich mit Edge geprüft: zwölf Sprachen,
Flaggen, Gruppen-/Monats-/Suchfilter, Export, Teilzahlungen, Sortierung und mobile
Darstellung. Eine echte PayPal-Verbindung wurde nicht getestet.

## Lizenz

MIT, siehe `LICENSE`.
