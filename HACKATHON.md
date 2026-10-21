# Hackathon preparation — working draft

## English project description
Cashflow Guardian helps small businesses review unpaid invoices without sending
financial records to an external AI provider. It combines PayPal sandbox invoice
retrieval with local similarity and anomaly detection. Users can explore aging
buckets, inspect the evidence behind a flag, review partial balances and prepare
an editable reminder. Twelve languages and locale-aware dates make the workbench
accessible across markets. Currency totals remain separate to avoid misleading sums.

## Two-minute demo outline
0:00–0:20: Explain the problem: finding the next safe action among many invoices.
0:20–0:45: Show the explicitly synthetic queue: possible duplicate, 37-day overdue
  invoice, missing due date and partial payment. Explain why the app does not send.
0:45–1:15: Open the possible duplicate; show the matching evidence and manual check.
  Then open the overdue example, inspect its balance and prepare an editable reminder.
1:15–1:40: Use AG Grid to filter, sort, resize and page through the same invoices.
1:40–2:00: Show the verified read-only Sandbox connection, then
  switch locale and explain the local-processing and forecast limitations.
Do not substitute synthetic offline screens for proof of a real PayPal connection.

## Evidence still required
- PayPal Sandbox connection has been verified locally and returned one test invoice;
  rerun it before recording. The synthetic data covers the richer walkthrough cases.
- Record a public YouTube video under three minutes after that validation.
- Complete English Devpost submission and verify eligibility with official rules.
- AG Grid Community is integrated in the invoice workspace and bundled locally.
  A server-side, synthetic-data-only OpenAI bridge is scaffolded but stays disabled
  until local environment settings are supplied. AG Studio's licensed Agent Framework
  and UI are not integrated; do not claim those Enterprise/Studio capabilities.
- There is no measured time-saving claim yet. For a fair pilot, have users identify
  the same overdue balances and duplicate candidates with their usual workflow and
  this app; record completion time, accuracy, sample size and median difference.
  Publish measured results and conditions, not estimates presented as evidence.

Product improvements chosen: aging buckets to prioritize follow-up, visible evidence
and manual review for AI signals, validated local imports and draft-only reminders.
Further development should follow observed customer problems before subscriptions.
The prototype currently has no billing, production payments or multi-user service.

Sources:
- Official competition rules: https://paypalaihackathon.devpost.com/rules
- Aging-report workflow: https://stripe.com/resources/more/what-is-an-aging-report-what-is-in-one-and-how-to-use-it
- PayPal Invoicing API: https://developer.paypal.com/api/invoicing/v2/
