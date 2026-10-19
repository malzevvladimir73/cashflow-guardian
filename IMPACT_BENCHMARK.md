# Measure the invoice-review benefit

**Status: protocol prepared; no time-saving result has been measured.** The bundled
benchmark records are fictional. Do not describe the expected answer key as a user
study or as proof that the product saves time.

## Repeatable task

Use the same 15 records for both methods: ordinary spreadsheet review and Cashflow
Guardian. The fixed dates are anchored to 2026-10-19; run this as a historical
benchmark only if the app supports that same as-of date. Otherwise regenerate or
use a fresh equivalent date set, then recompute the answer key before timing.

Ask each participant to:
1. List every unpaid invoice whose due date has passed.
2. Sum the outstanding amount in USD.
3. Note the aging bucket shown for each overdue invoice.
4. Inspect the proposed similar-invoice pair and decide whether it deserves human review.

Do not tell participants the answer key before both runs. Alternate the order of
spreadsheet and app runs across participants to reduce practice effects. Use the
same browser, dataset and instructions for both. Start timing when the task begins;
stop when the participant submits all four answers. Record wrong IDs, amount error,
missed seeded near-match and task time. Do not use live customer records.

## Dataset and answer key

Use the CSV for both methods: [benchmark/invoices_2026-10-19.csv](benchmark/invoices_2026-10-19.csv).
Import that same file into Cashflow Guardian and open it in your spreadsheet app.
A JSON copy is also provided. Every record is fictional.

As of 2026-10-19, the unpaid overdue IDs are INV-1024, INV-1026, INV-1028,
INV-1032, INV-1035 and INV-1036. Expected unpaid total: **USD 14,500**.
INV-1025, INV-1030, INV-1034 and INV-1038 are paid, so exclude them even though
some due dates have passed. INV-1029 is a draft, not an outstanding sent invoice.
INV-1024 and INV-1028 are a seeded near-match for manual review, not a confirmed
duplicate. Aging buckets change as calendar time passes; record the run date and
the app's displayed bucket for each record.

## Record results

| Participant | Method | Order | Time (seconds) | Correct overdue IDs | Total error (USD) | Near-match reviewed? |
|---|---|---|---:|---:|---:|---|
|  | Spreadsheet |  |  |  |  |  |
|  | Cashflow Guardian |  |  |  |  |  |

For each participant, compute time difference as spreadsheet time minus app time;
positive means the app run was faster. Report the median paired difference, task
accuracy, number of participants and test conditions. With one participant, call
it a single-person pilot. With a small convenience sample, do not generalize it to
all businesses. Publish results only after completing both runs. If timing fails
to improve or accuracy drops, report that plainly.

## Current evidence

The PayPal Sandbox integration was manually verified with two sent test invoices,
including one overdue example. That confirms invoice retrieval and the visible
overdue workflow. It does **not** measure user time saved or establish model
accuracy on real businesses.
