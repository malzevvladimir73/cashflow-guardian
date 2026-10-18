"""Local ML-based invoice intelligence: no external AI service or personal data sharing.

Uses sklearn TF-IDF character n-grams to find near-duplicate descriptions,
and IsolationForest to rank unusual invoice amounts/ages. Outputs are flags
for human review, NOT evidence of fraud and NOT payment instructions.
"""
from datetime import date

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

UNPAID = {"SENT", "UNPAID", "PARTIALLY_PAID", "PAYMENT_PENDING", "OVERDUE"}


def _dt(v):
    try:
        return date.fromisoformat((v or "")[:10])
    except (ValueError, TypeError):
        return None


def score_invoices(invoices, today=None):
    today = today or date.today()
    records = [dict(x) for x in invoices]
    if not records:
        return {"invoices": [], "duplicates": [], "summary": _summary([], [])}

    # Genuine machine learning for semantic duplicate matching.
    # Character n-grams accommodate spelling and punctuation variations.
    corpus = [str(x.get("description") or "Unknown") for x in records]
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), lowercase=True)
    vectors = vectorizer.fit_transform(corpus)
    similarity = cosine_similarity(vectors)
    pairs = []
    involved = set()
    for i in range(len(records)):
        for j in range(i + 1, len(records)):
            left, right = records[i], records[j]
            if left.get("currency") != right.get("currency"):
                continue
            if str(left.get("customer", "")).casefold() != str(right.get("customer", "")).casefold():
                continue
            ai, aj = float(left.get("amount") or 0), float(right.get("amount") or 0)
            if max(ai, aj) and abs(ai - aj) / max(ai, aj) > 0.02:
                continue
            day_a, day_b = _dt(left.get("issued")), _dt(right.get("issued"))
            if not day_a or not day_b or abs((day_a - day_b).days) > 14:
                continue
            sim = float(similarity[i, j])
            if sim >= 0.70:
                pairs.append({"first": str(left.get("number")), "second": str(right.get("number")), "similarity": round(sim, 3), "reason": "Similar descriptions, same customer, near-identical amount and dates. Review manually."})
                involved.update([i, j])

    # IsolationForest is an unsupervised ML anomaly model; comparison is per
    # currency, avoiding misleading differences between USD/EUR etc.
    anomalies = set()
    by_currency = {}
    for i, item in enumerate(records):
        by_currency.setdefault(item.get("currency", "USD"), []).append(i)
    for indices in by_currency.values():
        if len(indices) < 8:
            continue
        features = np.array([
            [np.log1p(max(0.0, float(records[i].get("amount") or 0))),
             max(0, min(365, (today - _dt(records[i].get("issued"))).days)) if _dt(records[i].get("issued")) else 0]
            for i in indices], dtype=float)
        predictions = IsolationForest(n_estimators=80, contamination=0.13, random_state=29).fit_predict(features)
        anomalies.update(index for index, pred in zip(indices, predictions) if pred == -1)

    for i, rec in enumerate(records):
        due = _dt(rec.get("due"))
        is_open = rec.get("status") in UNPAID
        overdue_days = max(0, (today - due).days) if due and is_open else 0
        flags = []
        if overdue_days:
            flags.append(f"{overdue_days} days overdue")
        if i in involved:
            flags.append("Potential duplicate")
        if i in anomalies:
            flags.append("Unusual amount or age (ML)")
        rec["days_overdue"] = overdue_days
        rec["flags"] = flags
        rec["risk"] = "High" if (overdue_days > 21 or (overdue_days and i in involved)) else "Medium" if flags else "Low"
    return {"invoices": records, "duplicates": pairs, "summary": _summary(records, pairs)}


def _summary(rows, duplicate_pairs):
    currencies = sorted(set(row.get("currency", "USD") for row in rows))
    totals = {}
    for currency in currencies:
        bucket = [i for i in rows if i.get("currency") == currency]
        totals[currency] = {
            "outstanding": round(sum(float(x.get("due_amount", x["amount"])) for x in bucket if x["status"] in UNPAID), 2),
            "overdue": round(sum(float(x.get("due_amount", x["amount"])) for x in bucket if x.get("days_overdue", 0) > 0), 2),
            "paid": round(sum(float(x["amount"]) for x in bucket if x["status"] == "PAID"), 2),
        }
    return {
        "invoice_count": len(rows), "flagged_count": sum(bool(i.get("flags")) for i in rows),
        "duplicate_pairs": len(duplicate_pairs), "totals_by_currency": totals,
        "disclaimer": "Local ML signals for review, not fraud or payment decisions. All financial actions require human approval."
    }


def answer_question(report, question):
    """Grounded, read-only query assistant. Rules route intent; ML flags supply evidence.

    Does not pretend to be a generative LLM. No raw invoice fields leave the server.
    """
    q = str(question or "").strip().lower()[:500]
    rows = report["invoices"]
    if not q:
        return "Ask about overdue invoices, duplicate candidates, high-risk invoices, or who owes the most."
    if "duplicat" in q or "doppel" in q or "similar" in q:
        p = report["duplicates"]
        if not p:
            return "No likely near-duplicate invoices were detected by the local text-similarity model."
        return "Possible duplicate pairs for human review: " + "; ".join(f"{x['first']} + {x['second']} ({x['similarity']:.0%} description similarity)" for x in p[:6]) + ". Similarity alone does not prove a duplicate charge."
    if "risk" in q or "attention" in q or "priorit" in q or "urgent" in q or "priority" in q:
        flagged = sorted([x for x in rows if x.get("flags")], key=lambda x: (x["risk"] == "High", x.get("days_overdue", 0)), reverse=True)
        if not flagged:
            return "No invoices currently have review flags."
        return "Review first: " + "; ".join(f"{x['number']} ({x['customer']}, {x['currency']} {x['amount']:,.2f}): {', '.join(x['flags'])}" for x in flagged[:5]) + ". These are suggestions, not automatic payment actions."
    if "overdue" in q or "late" in q or "überfällig" in q:
        vals = report["summary"]["totals_by_currency"]
        return "Overdue unpaid invoice amounts: " + (", ".join(f"{currency} {total['overdue']:,.2f}" for currency, total in vals.items()) or "none") + ". Based on invoice due dates and statuses; partial payments may require checking the original PayPal invoice."
    if "most" in q or "largest" in q or "biggest" in q or "highest" in q or "größt" in q:
        open_rows = [x for x in rows if x["status"] in UNPAID]
        if not open_rows:
            return "No open invoices were found."
        top = sorted(open_rows, key=lambda x: x.get("amount", 0), reverse=True)[:3]
        return "Largest open invoices (amounts are not comparable across currencies): " + "; ".join(f"{x['number']} for {x['customer']}: {x['currency']} {x['amount']:,.2f}" for x in top) + "."
    for inv in rows:
        if inv["number"].lower() in q:
            return f"{inv['number']}: {inv['customer']}, {inv['currency']} {inv['amount']:,.2f}; {inv['status']}; due {inv.get('due') or 'not provided'}. " + (", ".join(inv["flags"]) if inv["flags"] else "No review flags.")
    return "I can answer: Which invoices need attention? What is overdue? Find duplicates. Which is the largest open invoice? Or ask about a specific invoice number."
