"""Localhost-only HTTP server. PayPal Sandbox API calls are read-only."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs,urlsplit
from demo_data import demo_invoices
from intelligence import score_invoices,answer_question
from paypal_client import PayPalError,get_invoices,sandbox_configured

STATIC=Path(__file__).resolve().parent/"static"
MAX_BODY=4096

class Handler(BaseHTTPRequestHandler):
    server_version="CashflowGuardian/0.1"
    def _send(self,payload,status=200):
        data=json.dumps(payload,ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(data)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Content-Security-Policy","default-src 'none'")
        self.end_headers()
        self.wfile.write(data)
    def _static(self,filename,content_type):
        try:data=(STATIC/filename).read_bytes()
        except FileNotFoundError:return self._send({"error":"Not found"},404)
        self.send_response(200)
        self.send_header("Content-Type",content_type)
        self.send_header("Content-Length",str(len(data)))
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Cache-Control","no-store")
        self.end_headers()
        self.wfile.write(data)
    @staticmethod
    def _report(source):
        if source=="demo":return score_invoices(demo_invoices())
        if source=="sandbox":return score_invoices(get_invoices())
        raise ValueError("source must be demo or sandbox")
    def do_GET(self):
        p=urlsplit(self.path)
        if p.path in ("/","/index.html"):return self._static("index.html","text/html; charset=utf-8")
        if p.path=="/style.css":return self._static("style.css","text/css; charset=utf-8")
        if p.path=="/app.js":return self._static("app.js","application/javascript; charset=utf-8")
        if p.path=="/api/status":
            return self._send({"sandbox_configured":sandbox_configured(),"mode":"read-only","environment":"sandbox","ai":"TF-IDF and IsolationForest (local)"})
        if p.path=="/api/analyze":
            source=parse_qs(p.query).get("source",["demo"])[0]
            try:
                report=self._report(source);report["source"]=source
                return self._send(report)
            except ValueError as exc:return self._send({"error":str(exc)},400)
            except PayPalError as exc:return self._send({"error":str(exc)},502)
        return self._send({"error":"Not found"},404)
    def do_POST(self):
        if urlsplit(self.path).path!="/api/ask":return self._send({"error":"Not found"},404)
        try:
            size=int(self.headers.get("Content-Length","0"))
            if size<=0 or size>MAX_BODY:return self._send({"error":"Request size must be between 1 and 4096 bytes"},413)
            obj=json.loads(self.rfile.read(size))
            question=obj.get("question","")
            source=obj.get("source","demo")
            if not isinstance(question,str) or len(question)>500:
                return self._send({"error":"Invalid question"},400)
            return self._send({"answer":answer_question(self._report(source),question)})
        except (ValueError,TypeError,json.JSONDecodeError,AttributeError):
            return self._send({"error":"Invalid request"},400)
        except PayPalError as exc:return self._send({"error":str(exc)},502)
    def log_message(self,fmt,*args):
        if self.path=="/api/status":return
        super().log_message("%s %s",self.command,self.path.split("?")[0])

def start(host="127.0.0.1",port=8765):
    httpd=ThreadingHTTPServer((host,port),Handler)
    print(f"Cashflow Guardian: http://{host}:{port} (synthetic demo by default)")
    print("PayPal Sandbox integration is read-only; never share API secrets.")
    try:httpd.serve_forever()
    except KeyboardInterrupt:pass
    finally:httpd.server_close()

if __name__=="__main__":
    parser=argparse.ArgumentParser(description="Cashflow Guardian local demo")
    parser.add_argument("--port",type=int,default=8765)
    args=parser.parse_args()
    start(port=args.port)
