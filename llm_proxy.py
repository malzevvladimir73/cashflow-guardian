"""Opt-in server-side OpenAI Responses API bridge for synthetic demo data only."""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from demo_data import demo_invoices
from intelligence import score_invoices

API_URL = "https://api.openai.com/v1/responses"
MAX_QUESTION = 500


class LlmUnavailable(Exception):
    """The external model is not configured or did not return a usable response."""


def is_configured():
    return bool(os.environ.get("OPENAI_API_KEY", "").strip() and os.environ.get("OPENAI_MODEL", "").strip())


def _synthetic_context():
    """Return a bounded fictional evidence summary; never reads PayPal/import data."""
    report = score_invoices(demo_invoices())
    invoices = []
    for row in report.get("invoices", [])[:40]:
        invoices.append({key: row.get(key) for key in (
            "number", "customer", "description", "amount", "currency", "status",
            "issued", "due", "due_amount", "risk", "flags", "days_overdue"
        )})
    return json.dumps({"summary": report.get("summary", {}), "invoices": invoices}, ensure_ascii=False)


def ask_synthetic(question):
    """Ask the configured model about synthetic records; caller-supplied rows are never accepted."""
    if not is_configured():
        raise LlmUnavailable("Externe KI ist deaktiviert. OPENAI_API_KEY und OPENAI_MODEL müssen lokal eingerichtet sein.")
    if not isinstance(question, str) or not question.strip() or len(question) > MAX_QUESTION:
        raise ValueError("Ungültige Frage")

    payload = {
        "model": os.environ["OPENAI_MODEL"].strip(),
        "instructions": (
            "You are Cashflow Guardian's invoice review assistant. Use only the supplied "
            "fictional demo records. Do not invent facts, payments, legal advice, or "
            "financial certainty. Explain evidence, state uncertainty, and recommend "
            "human review. Never send messages or change invoices. Answer in the user's language."
        ),
        "input": "FICTIONAL SYNTHETIC DEMO RECORDS (not customer data):\n"
                 + _synthetic_context() + "\n\nUser question:\n" + question.strip(),
        "store": False,
        "max_output_tokens": 500,
    }
    request = Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"].strip(),
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:
            result = json.loads(response.read(1_000_000))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        # Do not include upstream body/URL or credentials in logs or user-facing errors.
        raise LlmUnavailable("Der externe KI-Dienst ist momentan nicht erreichbar.") from exc
    texts = []
    for output in result.get("output", []):
        if not isinstance(output, dict) or output.get("type") != "message":
            continue
        for block in output.get("content", []):
            if isinstance(block, dict) and block.get("type") == "output_text":
                texts.append(block.get("text", ""))
    answer = "\n".join(texts).strip()
    if not answer or len(answer) > 6000:
        raise LlmUnavailable("Die externe KI lieferte keine verwendbare Antwort.")
    return answer
