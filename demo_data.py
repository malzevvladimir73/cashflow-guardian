"""Fictitious demo data, never real customer information."""
from datetime import date, timedelta

def demo_invoices(today=None):
    today = today or date.today()
    specs = [
        ("INV-1024","Northstar Studio","Brand identity and visual guidelines",1850,"SENT",-51,-22),
        ("INV-1025","Lumen Market","Monthly ecommerce analytics dashboard",920,"PAID",-41,-11),
        ("INV-1026","Harbor Works","Website development sprint two",3200,"SENT",-34,-9),
        ("INV-1027","Velvet Cafe","Social media content design",480,"SENT",-16,13),
        ("INV-1028","Northstar Studio","Brand identity & visual guide lines",1850,"SENT",-50,-21),
        ("INV-1029","Bright Labs","Automation workflow build",1100,"DRAFT",-4,26),
        ("INV-1030","Kite & Co","One-time consulting session",350,"PAID",-26,-2),
        ("INV-1031","Harbor Works","Web development phase 3",2850,"SENT",-12,7),
        ("INV-1032","Aurora Media","Quarterly content strategy",740,"SENT",-28,-2),
        ("INV-1033","Lumen Market","Ecommerce analytics monthly reporting",920,"SENT",-7,23),
        ("INV-1034","Echo Garden","Product photography 40 images",1250,"PAID",-48,-20),
        ("INV-1035","Orchid Labs","Software integration annual plan",6400,"SENT",-67,-37),
        ("INV-1036","Velvet Cafe","Menu and brand icon updates",460,"SENT",-21,-1),
        ("INV-1037","Bright Labs","QA and release automation support",1050,"SENT",-14,16),
        ("INV-1038","Aurora Media","Content strategy quarterly planning",740,"PAID",-89,-60),
    ]
    return [
        {"id":n,"number":n,"customer":c,"email":"","description":d,"amount":float(a),
         "due_amount":float(a) if s!="PAID" else 0.0,"currency":"USD",
         "status":s,"issued":(today+timedelta(days=i)).isoformat(),
         "due":(today+timedelta(days=u)).isoformat(),"source":"synthetic demo"}
        for n,c,d,a,s,i,u in specs
    ]
