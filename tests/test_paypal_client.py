import base64
import json
import os
from datetime import date
from io import BytesIO
from unittest.mock import patch

import paypal_client


def sample_invoice():
    return {
        "id": "INV2-EXAMPLE", "status": "UNPAID",
        "detail": {"invoice_number": "0028", "invoice_date": "2026-10-02", "payment_term": {"due_date": "2026-10-23"}},
        "amount": {"currency_code": "EUR", "value": "240.50"},
        "primary_recipients": [{"billing_info": {"name": {"given_name": "Ada", "surname": "Example"}, "email_address": "example@example.invalid"}}],
        "items": [{"name": "Consulting"}],
    }


def test_invoice_normalization():
    x = paypal_client.normalize_invoice(sample_invoice())
    assert x["number"] == "0028"
    assert x["amount"] == 240.50
    assert x["currency"] == "EUR"
    assert x["customer"] == "Ada Example"
    assert x["status"] == "UNPAID"


def test_invoice_detail_is_bounded_and_excludes_file_urls():
    detail = paypal_client.normalize_invoice_detail({
        "items": [{"name": "Consulting", "description": "Review", "quantity": "2", "unit_amount": {"currency_code": "EUR", "value": "120.25"}}],
        "payments": [{"payment_date": "2026-10-20", "method": "PAYPAL", "amount": {"currency_code": "EUR", "value": "240.50"}}],
        "attachments": [{"reference_url": "https://example.invalid/private", "content_type": "application/pdf", "size": 2048}],
    })
    assert detail["items"][0]["unit_amount"] == {"value": 120.25, "currency": "EUR"}
    assert detail["transactions"][0]["type"] == "payment"
    assert detail["attachments"][0]["content_type"] == "application/pdf"
    assert "reference_url" not in detail["attachments"][0]


def test_invoice_detail_requires_safe_id(monkeypatch):
    monkeypatch.setenv("PAYPAL_SANDBOX_CLIENT_ID", "fake-id")
    monkeypatch.setenv("PAYPAL_SANDBOX_CLIENT_SECRET", "fake-secret")
    with patch.object(paypal_client, "_request") as request:
        try:
            paypal_client.get_invoice_detail("../production")
        except paypal_client.PayPalError as exc:
            assert "Invalid invoice ID" in str(exc)
        else:
            raise AssertionError("Expected unsafe invoice ID rejection")
        request.assert_not_called()


def test_missing_credentials_is_safe(monkeypatch):
    monkeypatch.delenv("PAYPAL_SANDBOX_CLIENT_ID", raising=False)
    monkeypatch.delenv("PAYPAL_SANDBOX_CLIENT_SECRET", raising=False)
    assert not paypal_client.sandbox_configured()
    try:
        paypal_client.get_invoices()
    except paypal_client.PayPalError as error:
        assert "Sandbox not configured" in str(error)
    else:
        raise AssertionError("Expected missing Sandbox configuration error")


def test_sandbox_oauth_and_read_only_list(monkeypatch):
    monkeypatch.setenv("PAYPAL_SANDBOX_CLIENT_ID", "fake-id")
    monkeypatch.setenv("PAYPAL_SANDBOX_CLIENT_SECRET", "fake-secret")
    actions = []
    def fake_request(path, token=None, basic=None, data=None, timeout=15):
        actions.append((path, token, basic, data))
        if path == "/v1/oauth2/token":
            assert basic == ("fake-id", "fake-secret")
            assert data == b"grant_type=client_credentials"
            return {"access_token": "SYNTHETIC_ACCESS_TOKEN"}
        assert path.startswith("/v2/invoicing/invoices?page=1")
        assert token == "SYNTHETIC_ACCESS_TOKEN"
        assert data is None  # no writes to PayPal
        return {"items": [sample_invoice()], "total_pages": 1}
    monkeypatch.setattr(paypal_client, "_request", fake_request)
    rows = paypal_client.get_invoices()
    assert len(rows) == 1
    assert rows[0]["number"] == "0028"
    assert len(actions) == 2
    assert all(p.startswith(("/v1/oauth2/token", "/v2/invoicing/invoices")) for p, *_ in actions)


def test_reject_arbitrary_urls():
    try:
        paypal_client._request("//api-m.paypal.com/v2/invoicing/invoices")
    except paypal_client.PayPalError as exc:
        assert "Invalid sandbox API path" in str(exc)
    else:
        raise AssertionError("Expected absolute URL rejection")
