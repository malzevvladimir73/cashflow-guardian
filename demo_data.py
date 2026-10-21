"""Entirely fictitious records: never use live customer or payment data."""
from datetime import date, timedelta


def demo_invoices(today=None):
    today = today or date.today()
    specs = [
        ("INV-1024", "Northstar Studio", "Brand identity and visual guidelines", 1850, "USD", "SENT", -51, -22),
        ("INV-1025", "Lumen Market", "Monthly ecommerce analytics dashboard", 920, "USD", "PAID", -41, -11),
        ("INV-1026", "Harbor Works", "Website development sprint two", 3200, "USD", "SENT", -34, -9),
        ("INV-1027", "Velvet Cafe", "Social media content design package", 480, "USD", "SENT", -16, 13),
        ("INV-1028", "Northstar Studio", "Brand identity & visual guide lines", 1850, "USD", "SENT", -50, -21),
        ("INV-1029", "Bright Labs", "Automation workflow build", 1100, "USD", "DRAFT", -4, 26),
        ("INV-1030", "Kite & Co", "One-time consulting session", 350, "USD", "PAID", -26, -2),
        ("INV-1031", "Harbor Works", "Web development phase 3", 2850, "USD", "SENT", -12, 7),
        ("INV-1032", "Aurora Media", "Quarterly content strategy", 740, "USD", "SENT", -28, -2),
        ("INV-1033", "Lumen Market", "Ecommerce analytics monthly reporting", 920, "USD", "SENT", -7, 23),
        ("INV-1034", "Echo Garden", "Product photography 40 images", 1250, "USD", "PAID", -48, -20),
        ("INV-1035", "Orchid Labs", "Software integration annual plan", 6400, "USD", "SENT", -67, -37),
        ("INV-1036", "Velvet Cafe", "Menu and brand icon updates", 460, "USD", "SENT", -21, -1),
        # This intentional missing date tests safe triage: never infer a due date.
        ("INV-1037", "Bright Labs", "QA and release automation support", 1050, "USD", "SENT", -14, None),
        ("INV-1038", "Aurora Media", "Content strategy quarterly planning", 740, "USD", "PAID", -89, -60),
    ]
    rows = []
    for number, customer, desc, amount, currency, status, start, due in specs:
        rows.append({
            "id": number, "number": number, "customer": customer,
            "email": "", "description": desc, "amount": float(amount),
            "currency": currency, "status": status,
            "issued": (today + timedelta(days=start)).isoformat(),
            "due": (today + timedelta(days=due)).isoformat() if due is not None else "",
            "source": "synthetic demo",
        })
    by_id = {row["id"]: row for row in rows}

    def item(name, quantity, unit_price, description=""):
        return {"name": name, "description": description, "quantity": str(quantity),
                "unit_amount": {"value": float(unit_price), "currency": "USD"}}

    def transaction(kind, days_ago, amount, note=""):
        return {"type": kind, "date": (today - timedelta(days=days_ago)).isoformat(),
                "method": "PayPal", "amount": {"value": float(amount), "currency": "USD"}, "note": note}

    def attachment(content_type, days_ago, size):
        return {"content_type": content_type,
                "created": (today - timedelta(days=days_ago)).isoformat(), "size": size}

    examples = {
        "INV-1024": {
            "items": [item("Brand discovery workshop", 1, 1250, "Stakeholder session and direction"),
                      item("Visual identity guidelines", 1, 600, "Final brand usage guide")],
            "transactions": [], "attachments": [attachment("application/pdf", 50, 184320)],
        },
        "INV-1025": {
            "items": [item("Monthly analytics dashboard", 1, 700),
                      item("Performance review", 2, 110, "Two review sessions")],
            "transactions": [transaction("payment", 38, 920, "Paid in full")], "attachments": [],
        },
        "INV-1026": {
            "items": [item("Development sprint", 2, 1200, "Two implementation weeks"),
                      item("Accessibility review", 1, 800)],
            "transactions": [transaction("payment", 18, 2000, "Deposit received")],
            "attachments": [attachment("application/pdf", 19, 286720)],
        },
        "INV-1027": {
            "items": [item("Social content package", 12, 30, "Twelve designed posts"),
                      item("Content calendar", 1, 120)], "transactions": [], "attachments": [],
        },
        "INV-1028": {
            "items": [item("Brand discovery workshop", 1, 1250),
                      item("Visual identity guidelines", 1, 600)],
            "transactions": [], "attachments": [attachment("application/pdf", 49, 184320)],
        },
        "INV-1030": {
            "items": [item("Consulting session", 2, 175, "Two-hour strategy session")],
            "transactions": [transaction("payment", 24, 350, "Paid in full")], "attachments": [],
        },
        "INV-1031": {
            "items": [item("Web development phase 3", 1, 2200), item("Release support", 5, 130)],
            "transactions": [transaction("payment", 6, 2000, "Part payment")], "attachments": [],
        },
        "INV-1033": {
            "items": [item("Monthly ecommerce reporting", 1, 920)],
            "transactions": [transaction("payment", 5, 920, "Paid in full"),
                             transaction("refund", 3, 120, "Credit for an amended report")],
            "attachments": [attachment("application/pdf", 6, 97280)],
        },
        "INV-1035": {
            "items": [item("Annual integration plan", 1, 4800),
                      item("Data migration", 16, 100, "Sixteen migration hours")],
            "transactions": [], "attachments": [attachment("application/pdf", 66, 512000),
                                                   attachment("application/pdf", 65, 245760)],
        },
    }
    for invoice_id, detail in examples.items():
        by_id[invoice_id]["invoice_detail"] = detail
    by_id["INV-1026"].update(status="PARTIALLY_PAID", due_amount=1200.0)
    by_id["INV-1031"].update(status="PARTIALLY_PAID", due_amount=850.0)
    return rows
