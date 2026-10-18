"""Read-only PayPal Sandbox Invoicing v2 client. Never calls production URLs."""
import base64
import json
import os
import math
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SANDBOX = "https://api-m.sandbox.paypal.com"
MAX_INVOICES = 400


class PayPalError(RuntimeError):
    pass


def sandbox_configured():
    return bool(os.environ.get("PAYPAL_SANDBOX_CLIENT_ID") and os.environ.get("PAYPAL_SANDBOX_CLIENT_SECRET"))


def _request(path, token=None, basic=None, data=None, timeout=15):
    # Never permit arbitrary URLs or production endpoints.
    if not path.startswith("/") or path.startswith("//"):
        raise PayPalError("Invalid sandbox API path")
    headers = {"Accept": "application/json", "User-Agent": "CashflowGuardianHackathon/0.1"}
    if token:
        headers["Authorization"] = "Bearer " + token
    if basic:
        headers["Authorization"] = "Basic " + base64.b64encode(":".join(basic).encode()).decode()
    if data is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    request = Request(SANDBOX + path, headers=headers, data=data, method="POST" if data is not None else "GET")
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except HTTPError as exc:
        # Keep errors generic to avoid leaking sensitive request details.
        if exc.code in (401, 403):
            if basic:
                raise PayPalError(f"Sandbox login failed (HTTP {exc.code}). Copy Client ID and Secret from the SAME Sandbox app, not the account email/password or Live app.") from exc
            raise PayPalError(f"Sandbox invoice access denied (HTTP {exc.code}). App login succeeded, but invoice access failed. Check the associated Sandbox Business account and Invoicing access.") from exc
        raise PayPalError(f"PayPal Sandbox returned HTTP {exc.code}") from exc
    except (URLError, TimeoutError) as exc:
        raise PayPalError("Could not connect to PayPal Sandbox") from exc
    except ValueError as exc:
        raise PayPalError("Sandbox returned invalid JSON") from exc


def get_invoices():
    """Fetch at most 400 invoices; read-only list endpoint and OAuth token."""
    if not sandbox_configured():
        raise PayPalError("Sandbox not configured. Set PAYPAL_SANDBOX_CLIENT_ID and PAYPAL_SANDBOX_CLIENT_SECRET")
    auth = _request("/v1/oauth2/token", basic=(
        os.environ["PAYPAL_SANDBOX_CLIENT_ID"], os.environ["PAYPAL_SANDBOX_CLIENT_SECRET"]
    ), data=b"grant_type=client_credentials")
    token = auth.get("access_token")
    if not token:
        raise PayPalError("Sandbox did not return an access token")
    items = []
    for page in range(1, 5):
        qs = urlencode({"page": page, "page_size": 100, "total_required": "true"})
        batch = _request("/v2/invoicing/invoices?" + qs, token=token)
        records = batch.get("items", [])
        if not isinstance(records, list):
            raise PayPalError("Unexpected invoice response from Sandbox")
        items.extend(records)
        total_pages = batch.get("total_pages")
        if len(records) < 100 or (total_pages is not None and page >= int(total_pages)):
            break
        if page == 4:
            raise PayPalError('More than 400 invoices: analysis stopped to avoid incomplete totals.')
    return [normalize_invoice(item) for item in items[:MAX_INVOICES]]


def _amount(value):
    if isinstance(value, dict):
        value = value.get("value", 0)
    try:
        amount = float(value)
        if not math.isfinite(amount) or amount < 0 or amount > 1_000_000_000:
            raise PayPalError('Invalid invoice amount')
        return amount
    except (ValueError, TypeError) as exc:
        raise PayPalError('Invalid invoice amount') from exc


def normalize_invoice(inv):
    detail = inv.get("detail") or {}
    money = inv.get("amount") or inv.get("due_amount") or {}
    billing_info = inv.get("primary_recipients") or []
    bill_to = billing_info[0].get("billing_info", {}) if billing_info else {}
    name = bill_to.get("name") or {}
    recipient = " ".join([str(name.get("given_name") or ""), str(name.get("surname") or "")]).strip()
    recipient = recipient or str(bill_to.get("email_address") or "Customer")
    items = inv.get("items") or []
    item_names = ", ".join(str(i.get("name") or "") for i in items)
    return {
        "id": str(inv.get("id") or detail.get("invoice_number") or "unknown"),
        "number": str(detail.get("invoice_number") or inv.get("id") or "unknown"),
        "customer": recipient,
        "email": str(bill_to.get("email_address") or ""),
        "description": item_names or str(detail.get("memo") or "Services"),
        "amount": _amount(money),
        "due_amount": _amount(inv.get("due_amount") if inv.get("due_amount") is not None else (0 if inv.get('status') in ('PAID', 'MARKED_AS_PAID') else money)),
        "currency": str(money.get("currency_code") or "USD") if isinstance(money, dict) else "USD",
        "status": str(inv.get("status") or "DRAFT").upper(),
        "issued": str(detail.get("invoice_date") or "")[:10],
        "due": str((detail.get("payment_term") or {}).get("due_date") or "")[:10],
        "source": "sandbox",
    }
