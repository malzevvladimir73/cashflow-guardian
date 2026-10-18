import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import pytest
from server import Handler
from validation import validate_invoices
from paypal_client import _amount, PayPalError, normalize_invoice
from intelligence import score_invoices

def sample():
    return {'number': 'LOCAL-1', 'customer': 'Example', 'description': '',
            'amount': 100, 'due_amount': 40, 'currency': 'EUR',
            'status': 'PARTIALLY_PAID', 'issued': '2026-01-01', 'due': '2026-01-31'}

@pytest.mark.parametrize('value', [float('nan'), float('inf'), -1, 1e12])
def test_reject_unsafe_amounts(value):
    with pytest.raises((ValueError, PayPalError)):
        _amount(value)

@pytest.mark.parametrize('field,value', [('due','2026-02-30'), ('amount','NaN'), ('due_amount',101), ('number',''), ('currency','<script>'), ('status','UNKNOWN')])
def test_import_validation(field,value):
    row=sample();row[field]=value
    with pytest.raises(ValueError):validate_invoices([row])

def test_import_drops_untrusted_fields_and_duplicate_numbers():
    row=sample();row['flags']=['Fake'];row['email']='private@example.invalid'
    result=validate_invoices([row])[0]
    assert 'flags' not in result and 'email' not in result
    assert result['due_amount']==40
    with pytest.raises(ValueError):validate_invoices([row,row])

def test_paid_missing_due_and_null_payment_term():
    row=normalize_invoice({'amount':{'value':'10','currency_code':'EUR'},'status':'PAID','detail':{'payment_term':None}})
    assert row['due_amount']==0 and row['due']==''

def test_partial_payment_totals_and_zero_outstanding():
    row=sample()
    result=score_invoices([row])
    totals=result['summary']['totals_by_currency']['EUR']
    assert totals['outstanding']==40 and totals['paid']==60
    row['due_amount']=0
    result=score_invoices([row])
    assert result['invoices'][0]['days_overdue']==0

def test_more_than_400_is_not_silently_truncated(monkeypatch):
    import paypal_client
    monkeypatch.setenv('PAYPAL_SANDBOX_CLIENT_ID','fake')
    monkeypatch.setenv('PAYPAL_SANDBOX_CLIENT_SECRET','fake')
    monkeypatch.setattr(paypal_client,'_request',lambda path,**kw: {'access_token':'fake'} if 'oauth2' in path else {'items':[{}]*100,'total_pages':5})
    with pytest.raises(PayPalError,match='400'):paypal_client.get_invoices()

def test_host_origin_and_import_endpoint():
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    try:
        for headers in [{'Host':'attacker.invalid'}, {'Origin':'https://attacker.invalid'}, {'Sec-Fetch-Site':'cross-site'}]:
            with pytest.raises(HTTPError) as e:urlopen(Request(base+'/api/status',headers=headers),timeout=5)
            assert e.value.code==403
        req=Request(base+'/api/import',data=json.dumps([sample()]).encode(),headers={'Content-Type':'application/json'})
        with urlopen(req,timeout=10) as response:
            data=json.load(response)
        assert data['source']=='import'
        assert data['summary']['totals_by_currency']['EUR']['outstanding']==40
        with urlopen(base) as response:assert "frame-ancestors 'none'" in response.headers['Content-Security-Policy']
        with pytest.raises(HTTPError) as e:urlopen(Request(base+'/api/import',data=b'[]'),timeout=5)
        assert e.value.code==415
    finally:server.shutdown();server.server_close();thread.join()
