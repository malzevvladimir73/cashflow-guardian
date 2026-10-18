# Hackathon preparation — working draft

## English project description
Cashflow Guardian helps small businesses review unpaid invoices without sending
financial records to an external AI provider. It combines PayPal sandbox invoice
retrieval with local similarity and anomaly detection. Users can explore aging
buckets, inspect the evidence behind a flag, review partial balances and prepare
an editable reminder. Twelve languages and locale-aware dates make the workbench
accessible across markets. Currency totals remain separate to avoid misleading sums.

## Two-minute demo outline
0:00–0:20: Explain the problem: finding actionable overdue invoices among many rows.
0:20–0:45: Show a real sandbox dataset after completing SANDBOX_SETUP.md. Identify it
as test data. Do not show credentials or unrelated customer information.
0:45–1:15: Select a currency, filter overdue aging and open an invoice. Explain the
remaining balance and similarity/anomaly signal, including human review limits.
1:15–1:40: Draft a reminder, show that nothing is sent automatically; switch locale
and demonstrate date settings and a group/month filter.
1:40–2:00: Explain local processing, show repository/setup instructions and limitations.
Do not substitute synthetic offline screens for proof of a real PayPal connection.

## Evidence still required
- Create sandbox app, populate fictional invoices and verify API results end to end.
- Record a public YouTube video under three minutes after that validation.
- Complete English Devpost submission and verify eligibility with official rules.
- AG Grid special prize: not currently implemented; do not claim this integration.
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
