# Cashflow Guardian — Hackathon demo runbook

Use synthetic invoices for the product walkthrough. Use the PayPal Sandbox only to
prove the live read-only connection. Do not show real customer or payment data.

## 1. Verify the build

On a clean Windows checkout, install Python dependencies once with `SETUP_WINDOWS.bat`.
Then run `python -m pytest -q`; the expected result is all tests passing. Start the
local app with `START_SERVER.bat` and open `http://127.0.0.1:8765`. The app should
open in Synthetic Demo mode with 15 clearly fictional invoices.

## 2. Walk through the useful cases

1. Open AI Insights and show the evidence-based queue. Explain that flags are review
   suggestions, not fraud findings or automatic decisions.
2. Open `INV-1024` and `INV-1028` as a possible duplicate pair. Compare the customer,
   amount, date and similar descriptions; leave the decision to a person.
3. Open `INV-1035` to show the 37-day-overdue example, the outstanding amount and
   the editable reminder draft. Do not send the draft.
4. Show `INV-1037` with its missing due date and `INV-1031` with its partial balance.
5. Use the AG Grid table to filter, sort and group the same synthetic records.
6. Change currency or locale and explain that different currencies are not added.

Expected synthetic scenarios: possible duplicate, long-overdue invoice, missing due
date, partial payment and upcoming due date. The local ML and rule-based analysis
works without any external model key or network access.

## 3. Prove PayPal Sandbox separately

1. Follow `SANDBOX_SETUP.md` and start `START_SANDBOX.bat`.
2. Enter Sandbox credentials only in the local hidden-input prompt. Never record the
   prompt, credentials, account email or any personal invoice fields.
3. Select PayPal Sandbox in the app and confirm that the test invoice is returned.
   The connection was previously verified locally with one test invoice; rerun it
   before recording so the video shows current evidence.
4. Switch back to Synthetic Demo before showing detailed invoice scenarios.

The PayPal integration is read-only. It does not create invoices, payments or
reminders. External AI is disabled by default; the optional server bridge is limited
to synthetic demo records and is not required for this walkthrough.

## 4. Record and submit

Keep the video under three minutes. Show the working application on Windows, state
the problem and target user, demonstrate the main cases and finish with the PayPal
Sandbox connection and privacy boundary. Use English narration or provide an English
translation/subtitles. Use no copyrighted music or unlicensed third-party material.

Submit the public repository URL, the public YouTube link, an English project
description and complete run instructions through the Devpost submission form.
