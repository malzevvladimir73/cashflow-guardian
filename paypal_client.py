"""Read-only PayPal Sandbox Invoicing v2 client. Never calls production URLs."""
import base64
import json
import os
import math
import re
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

SANDBOX = "https://api-m.sandbox.paypal.com"
MAX_INVOICES = 400


class PayPalError(RuntimeError):
    pass


def _error_diagnostic(exc):
    # Only expose bounded machine identifiers, never response text or credentials.
    try:
        payload = json.loads(exc.read(16384))
    except (ValueError, OSError):
        return ' PayPal code: unavailable.'
    if not isinstance(payload, dict):
        return ' PayPal code: unavailable.'
    name = payload.get('name', '')
    debug = payload.get('debug_id', '')
    name = name if isinstance(name, str) and re.fullmatch(r'[A-Z_]{3,80}', name) else 'unavailable'
    debug = debug if isinstance(debug, str) and re.fullmatch(r'[a-fA-F0-9]{8,64}', debug) else 'unavailable'
    return f' PayPal code: {name}; Debug ID: {debug}.'


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
            raise PayPalError(f"Sandbox invoice access denied (HTTP {exc.code}). App login succeeded, but invoice access failed." + _error_diagnostic(exc)) from exc
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


def _access_token():
    if not sandbox_configured():
        raise PayPalError("Sandbox not configured. Set PAYPAL_SANDBOX_CLIENT_ID and PAYPAL_SANDBOX_CLIENT_SECRET")
    auth = _request("/v1/oauth2/token", basic=(
        os.environ["PAYPAL_SANDBOX_CLIENT_ID"], os.environ["PAYPAL_SANDBOX_CLIENT_SECRET"]
    ), data=b"grant_type=client_credentials")
    token = auth.get("access_token")
    if not token:
        raise PayPalError("Sandbox did not return an access token")
    return token


def get_invoice_detail(invoice_id):
    """Fetch safe, read-only details for one invoice in PayPal Sandbox."""
    if not isinstance(invoice_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", invoice_id):
        raise PayPalError("Invalid invoice ID")
    token = _access_token()
    payload = _request("/v2/invoicing/invoices/" + quote(invoice_id, safe=""), token=token)
    if not isinstance(payload, dict):
        raise PayPalError("Unexpected invoice detail response from Sandbox")
    return normalize_invoice_detail(payload)


def _safe_text(value, limit=300):
    return value[:limit] if isinstance(value, str) else ""


def _safe_money(value):
    if not isinstance(value, dict):
        return None
    try:
        amount = _amount(value)
        currency = value.get("currency_code")
        if not isinstance(currency, str) or not re.fullmatch(r"[A-Z]{3}", currency):
            return None
        return {"value": amount, "currency": currency}
    except PayPalError:
        return None


def normalize_invoice_detail(inv):
    items = []
    for item in inv.get("items") or []:
        if not isinstance(item, dict) or len(items) >= 100:
            continue
        items.append({
            "name": _safe_text(item.get("name"), 200),
            "description": _safe_text(item.get("description"), 500),
            "quantity": _safe_text(str(item.get("quantity", "")), 30),
            "unit_amount": _safe_money(item.get("unit_amount")),
            "amount": _safe_money(item.get("unit_amount")),
        })
    transactions = []
    for kind in ("payments", "refunds"):
        source = inv.get(kind) or []
        if not isinstance(source, list):
            continue
        for payment in source[:100]:
            if not isinstance(payment, dict):
                continue
            amount = _safe_money(payment.get("amount"))
            if amount:
                transactions.append({
                    "type": kind[:-1],
                    "date": _safe_text(payment.get("payment_date") or payment.get("refund_date") or payment.get("date"), 40),
                    "method": _safe_text(payment.get("method"), 80),
                    "amount": amount,
                    "note": _safe_text(payment.get("note"), 300),
                })
    attachments = []
    for attachment in inv.get("attachments") or []:
        if not isinstance(attachment, dict) or len(attachments) >= 100:
            continue
        size = attachment.get("size")
        attachments.append({
            "content_type": _safe_text(attachment.get("content_type"), 100),
            "created": _safe_text(attachment.get("create_time"), 40),
            "size": size if isinstance(size, int) and 0 <= size <= 2_000_000_000 else None,
        })
    return {"items": items, "transactions": transactions, "attachments": attachments}


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
