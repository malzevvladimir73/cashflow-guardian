# Cashflow Guardian 0.9

A local invoice review workbench with twelve languages, currency-separated totals,
aging buckets, interactive charts, invoice details and reminder drafts.

## Try it
Open `Cashflow_Guardian_v0.9.html` (or `Cashflow_Guardian_Demo.html`). No install is
needed. Included invoices are fictional. Import your own CSV using the downloadable
template, or a JSON array. Imported records remain in memory; settings alone are
stored in the browser. Exported files must be protected by their owner.

For local machine learning, install Python 3.11+ and run:

```console
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python server.py
```

On Windows, `SETUP_WINDOWS.bat` installs these dependencies; then use
`START_SERVER.bat`. Open the localhost address printed by the server.
For PayPal use `START_SANDBOX.bat` and follow [SANDBOX_SETUP.md](SANDBOX_SETUP.md).
The app reads sandbox invoices; it never initiates payments or sends reminders.

## What changed
- Removed the duplicate header settings button and misleading default currency.
- The overview currency selector refreshes totals, alerts, charts and invoice rows.
  Different currencies are never added together or converted.
- Aging buckets: current, 1–30, 31–60, 61–90 and 90+ days overdue.
- Invoice details, similarity evidence, session-only review marks and editable,
  multilingual reminder drafts. Copying a draft does not send it.
- CSV/JSON import with limits, date/amount validation and no automatic persistence.
- Partial payments split into paid and outstanding amounts.
- Twelve languages and flags, grouping, monthly filtering and CSV export retained.
- Date preferences initially follow browser locale, not inferred physical location.
  Settings allow US, European, ISO and compact formats; exports use ISO dates.

## Analysis and boundaries
The Python server uses TF-IDF similarity and IsolationForest to flag items for
human review. These are heuristic signals, not fraud findings or credit scores.
The offline demo contains precomputed example signals; offline imports use due-date
rules only. The assistant answers supported questions from invoice data, not an
external language model. No invoices are uploaded to an AI provider.

The monthly chart represents invoice due dates, not actual cash receipts. Dashboard
totals apply to the selected currency; table filters narrow the displayed rows.
Imports accept 1–1,000 rows and at most 2 MB; PayPal reads at most 400 invoices and
fails instead of silently showing incomplete totals beyond that limit.

This is a local prototype, not a hosted multi-user accounting or payment service.
Real PayPal sandbox verification is pending account setup. AG Grid is not integrated.
See [SECURITY.md](SECURITY.md) and [HACKATHON.md](HACKATHON.md).

## Development
Edit `static/` and Python sources; run `python build_offline.py` to regenerate the
latest HTML and demo. Earlier HTML versions are retained. Build input v0.6 contains
only synthetic invoices. Do not replace it with private financial data.

```console
python -m pytest -q
python build_offline.py
```

Validation: 27 Python tests; Edge checks for offline and server imports, malformed
input, currency totals, details, draft/review, aging, twelve languages and mobile
navigation. Actual PayPal connectivity has not been tested with credentials.
GitHub Actions checks tests and reproducible HTML. Make changes on a branch and
submit a pull request. Never commit credentials, financial exports or environments.

MIT license; see LICENSE.
