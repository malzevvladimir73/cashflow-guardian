"""Local ML invoice intelligence. No external AI service or personal data sharing."""
from datetime import date
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

UNPAID={"SENT","UNPAID","PARTIALLY_PAID","PAYMENT_PENDING","OVERDUE"}

def _dt(v):
    try: return date.fromisoformat((v or "")[:10])
    except (ValueError,TypeError): return None

def score_invoices(invoices,today=None):
    today=today or date.today()
    records=[dict(x) for x in invoices]
    if not records:
        return {"invoices":[],"duplicates":[],"summary":_summary([],[])}
    corpus=[str(x.get("description") or "Unknown") for x in records]
    vectors=TfidfVectorizer(analyzer="char_wb",ngram_range=(2,5),lowercase=True).fit_transform(corpus)
    similarity=cosine_similarity(vectors)
    pairs=[]
    involved=set()
    for i in range(len(records)):
        for j in range(i+1,len(records)):
            a,b=records[i],records[j]
            if a.get("currency")!=b.get("currency"): continue
            if str(a.get("customer","")).casefold()!=str(b.get("customer","")).casefold(): continue
            x,y=float(a.get("amount") or 0),float(b.get("amount") or 0)
            if max(x,y) and abs(x-y)/max(x,y)>0.02: continue
            da,db=_dt(a.get("issued")),_dt(b.get("issued"))
            if not da or not db or abs((da-db).days)>14:continue
            sim=float(similarity[i,j])
            if sim>=0.70:
                pairs.append({"first":str(a.get("number")),"second":str(b.get("number")),"similarity":round(sim,3),"reason":"Similar descriptions, customer, amount and dates. Review manually."})
                involved.update((i,j))
    anomalies=set()
    by_currency={}
    for i,rec in enumerate(records):
        by_currency.setdefault(rec.get("currency","USD"),[]).append(i)
    for indices in by_currency.values():
        if len(indices)<8:continue
        features=np.array([[np.log1p(max(0.,float(records[i].get("amount") or 0))),
                            max(0,min(365,(today-_dt(records[i].get("issued"))).days)) if _dt(records[i].get("issued")) else 0]
                           for i in indices],dtype=float)
        predictions=IsolationForest(n_estimators=80,contamination=0.13,random_state=29).fit_predict(features)
        anomalies.update(i for i,pred in zip(indices,predictions) if pred==-1)
    for i,rec in enumerate(records):
        due=_dt(rec.get("due"))
        overdue=max(0,(today-due).days) if due and rec.get("status") in UNPAID else 0
        flags=[]
        if overdue:flags.append(f"{overdue} days overdue")
        if i in involved:flags.append("Potential duplicate")
        if i in anomalies:flags.append("Unusual amount or age (ML)")
        rec["days_overdue"]=overdue
        rec["flags"]=flags
        rec["risk"]="High" if overdue>21 or (overdue and i in involved) else "Medium" if flags else "Low"
    return {"invoices":records,"duplicates":pairs,"summary":_summary(records,pairs)}

def _summary(rows,pairs):
    totals={}
    for currency in sorted(set(row.get("currency","USD") for row in rows)):
        bucket=[x for x in rows if x.get("currency")==currency]
        totals[currency]={
            "outstanding":round(sum(float(x.get("due_amount",x["amount"])) for x in bucket if x["status"] in UNPAID),2),
            "overdue":round(sum(float(x.get("due_amount",x["amount"])) for x in bucket if x.get("days_overdue",0)>0),2),
            "paid":round(sum(float(x["amount"]) for x in bucket if x["status"]=="PAID"),2)
        }
    return {"invoice_count":len(rows),"flagged_count":sum(bool(x.get("flags")) for x in rows),
            "duplicate_pairs":len(pairs),"totals_by_currency":totals,
            "disclaimer":"Local ML signals for review, not fraud or payment decisions. Human approval required."}

def answer_question(report,question):
    q=str(question or "").strip().lower()[:500]
    rows=report["invoices"]
    if not q:return "Ask about overdue invoices, duplicates, high-risk invoices, or who owes the most."
    if any(s in q for s in ("duplicat","doppel","similar")):
        pairs=report["duplicates"]
        return ("Possible duplicates for human review: "+"; ".join(f"{x['first']} + {x['second']} ({x['similarity']:.0%} similarity)" for x in pairs[:6])+".") if pairs else "No likely duplicates detected."
    if any(s in q for s in ("risk","attention","priorit","urgent")):
        found=sorted([x for x in rows if x.get("flags")],key=lambda x:(x["risk"]=="High",x["days_overdue"]),reverse=True)
        return "Review first: "+"; ".join(f"{x['number']} ({x['customer']}): {', '.join(x['flags'])}" for x in found[:5]) if found else "No flagged invoices."
    if any(s in q for s in ("overdue","late","überfällig")):
        return "Overdue unpaid amounts: "+", ".join(f"{ccy} {x['overdue']:,.2f}" for ccy,x in report["summary"]["totals_by_currency"].items())
    if any(s in q for s in ("most","largest","biggest","highest","größt")):
        found=sorted([x for x in rows if x["status"] in UNPAID],key=lambda x:x.get("amount",0),reverse=True)
        return "Largest open invoices (currencies not comparable): "+"; ".join(f"{x['number']} for {x['customer']}: {x['currency']} {x['amount']:,.2f}" for x in found[:3]) if found else "No open invoices."
    for x in rows:
        if x["number"].lower() in q:
            return f"{x['number']}: {x['customer']}, {x['currency']} {x['amount']:,.2f}; {x['status']}; due {x.get('due') or 'unknown'}. "+(", ".join(x["flags"]) if x["flags"] else "No review flags.")
    return "Ask about overdue invoices, duplicates, highest open amount, risk, or an invoice number."
