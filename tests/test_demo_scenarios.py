from datetime import date

from demo_data import demo_invoices
from intelligence import score_invoices


def test_synthetic_demo_covers_action_assistant_cases():
    today = date(2026, 10, 21)
    rows = demo_invoices(today)
    by_number = {row["number"]: row for row in rows}

    assert len(rows) == 15
    assert by_number["INV-1037"]["due"] == ""
    assert by_number["INV-1031"]["status"] == "PARTIALLY_PAID"
    assert by_number["INV-1031"]["due_amount"] == 850.0
    assert by_number["INV-1027"]["due"] == "2026-11-03"

    report = score_invoices(rows, today)
    pair = {frozenset((item["first"], item["second"])) for item in report["duplicates"]}
    assert frozenset(("INV-1024", "INV-1028")) in pair
    assert report["invoices"][11]["days_overdue"] == 37
    assert report["invoices"][11]["risk"] == "High"
