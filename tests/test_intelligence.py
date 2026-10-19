from datetime import date
from demo_data import demo_invoices
from intelligence import answer_question, score_invoices

TODAY = date(2026, 10, 18)


def test_local_ml_flags_duplicate():
    report = score_invoices(demo_invoices(TODAY), TODAY)
    pair_numbers = {frozenset([x["first"], x["second"]]) for x in report["duplicates"]}
    assert frozenset(["INV-1024", "INV-1028"]) in pair_numbers
    assert report["summary"]["invoice_count"] == 15
    assert report["summary"]["flagged_count"] >= 3


def test_overdue_excludes_paid_and_draft():
    report = score_invoices(demo_invoices(TODAY), TODAY)
    assert report["summary"]["totals_by_currency"]["USD"]["overdue"] > 0
    assert all(row["days_overdue"] == 0 for row in report["invoices"] if row["status"] in ("PAID", "DRAFT"))


def test_assistant_is_grounded():
    report = score_invoices(demo_invoices(TODAY), TODAY)
    assert "INV-1024" in answer_question(report, "Find duplicates")
    assert "USD" in answer_question(report, "What is overdue?")
    assert "INV-1035" in answer_question(report, "What is the largest open invoice?")
    assert "Northstar Studio" in answer_question(report, "What about INV-1024?")


def test_empty_dataset():
    r = score_invoices([])
    assert r["summary"]["invoice_count"] == 0
    assert r["duplicates"] == []
