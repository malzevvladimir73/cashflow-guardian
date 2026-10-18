"""Read-only PayPal Sandbox Invoicing v2 API client. Never calls production."""
import base64
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SANDBOX = "https://api-m.sandbox.paypal.com"
class PayPalError(RuntimeError):
    pass

def sandbox_configured():
    return bool(os.environ.get("PAYPAL_SANDBOX_CLIENT_ID") and os.environ.get("PAYPAL_SANDBOX_CLIENT_SECRET"))

def _request(path, token=None, basic=None, data=None, timeout=15):
    if not path.startswith("/") or path.startswith("//"):
        raise PayPalError("Invalid sandbox API path")
    headers = {"Accept":"application/json","User-Agent":"CashflowGuardianHackathon/0.1"}
    if token:
        headers["Authorization"] = "Bearer " + token
    if basic:
        headers["Authorization"] = "Basic " + base64.b64encode(":".join(basic).encode()).decode()
    if data is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = Request(SANDBOX + path, headers=headers, data=data, method="POST" if data is not None else "GET")
    try:
        with urlopen(req, timeout=timeout) as response:
            return json.load(response)
    except HTTPError as exc:
        if exc.code in (401,403):
            raise PayPalError("Sandbox authorization failed; check client credentials and permissions") from exc
        raise PayPalError(f"PayPal Sandbox returned HTTP {exc.code}") from exc
    except (URLError,TimeoutError) as exc:
        raise PayPalError("Could not connect to PayPal Sandbox") from exc
    except ValueError as exc:
        raise PayPalError("Sandbox returned invalid JSON") from exc

def _amount(val):
    if isinstance(val,dict): val=val.get("value",0)
    try: return max(0.,round(float(val),2))
    except (TypeError,ValueError): return 0.

def normalize_invoice(inv):
    detail=inv.get("detail") or {}
    money=inv.get("amount") or inv.get("due_amount") or {}
    rec=(inv.get("primary_recipients") or [{}])[0].get("billing_info") or {}
    name=rec.get("name") or {}
    customer=(" ".join([str(name.get("given_name") or ""),str(name.get("surname") or "")]).strip() or str(rec.get("email_address") or "Customer"))
    return {"id":str(inv.get("id") or detail.get("invoice_number") or "unknown"),
            "number":str(detail.get("invoice_number") or inv.get("id") or "unknown"),
            "customer":customer,"email":str(rec.get("email_address") or ""),
            "description":", ".join(str(i.get("name") or "") for i in (inv.get("items") or [])) or str(detail.get("memo") or "Services"),
            "amount":_amount(money),"due_amount":_amount(inv.get("due_amount") or money),
            "currency":str(money.get("currency_code") or "USD") if isinstance(money,dict) else "USD",
            "status":str(inv.get("status") or "DRAFT").upper(),
            "issued":str(detail.get("invoice_date") or "")[:10],
            "due":str((detail.get("payment_term") or {}).get("due_date") or "")[:10],
            "source":"sandbox"}

def get_invoices():
    if not sandbox_configured():
        raise PayPalError("Sandbox not configured; set PAYPAL_SANDBOX_CLIENT_ID and PAYPAL_SANDBOX_CLIENT_SECRET")
    auth=_request("/v1/oauth2/token",basic=(os.environ["PAYPAL_SANDBOX_CLIENT_ID"],os.environ["PAYPAL_SANDBOX_CLIENT_SECRET"]),data=b"grant_type=client_credentials")
    token=auth.get("access_token")
    if not token: raise PayPalError("Sandbox did not return an access token")
    items=[]
    for page in range(1,5):
        qs=urlencode({"page":page,"page_size":100,"total_required":"true"})
        result=_request("/v2/invoicing/invoices?"+qs,token=token)
        records=result.get("items",[])
        if not isinstance(records,list): raise PayPalError("Unexpected invoice response")
        items.extend(records)
        if len(records)<100 or (result.get("total_pages") is not None and page>=int(result["total_pages"])):break
    return [normalize_invoice(x) for x in items[:400]]
