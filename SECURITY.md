# Security boundaries

Run only on localhost on a trusted personal computer. This prototype has no user
accounts, tenant isolation, production payment processing or hosted deployment model.
Do not expose its port to the internet. Browser extensions and other local programs
are outside its security boundary.

The server checks Host, Origin and cross-site request metadata; it restricts JSON
requests and upload size and serves a content security policy. User text is escaped.
CSV exports neutralize spreadsheet formula prefixes. Imports validate dates, bounds,
statuses and duplicate IDs before analysis. These protections are tested, but are
not a substitute for an independent security audit.

PayPal endpoints are hardcoded to sandbox. Credentials live in process environment
only when entered through the starter. Invoice data is processed in memory, not
written to application storage. Browser preferences contain no invoices. Exported
CSV files are explicitly saved by the user. Application logs omit query strings.
Do not publish invoices, tokens, screenshots containing customer data or .env files.

Reminder drafts require human review and manual sending outside this application.
Review marks are temporary; they do not change PayPal records. ML flags can produce
false positives and false negatives. Do not use them as automatic collection decisions.

Guidance used:
- OWASP CSRF prevention: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- NIST transparency and human oversight: https://airc.nist.gov/airmf-resources/airmf/3-sec-characteristics/

Before commercial hosting: add authentication, tenant isolation, encrypted storage,
retention/deletion controls, monitored backups, authorization tests, independent
security review, and production PayPal onboarding. No production readiness claim.
