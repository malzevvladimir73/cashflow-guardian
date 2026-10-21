"""Zero-dependency HTTP server for Cashflow Guardian (localhost only)."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from demo_data import demo_invoices
from intelligence import answer_question, score_invoices
from llm_proxy import LlmUnavailable, ask_synthetic, is_configured
from paypal_client import PayPalError, get_invoice_detail, get_invoices, sandbox_configured
from validation import validate_invoices

STATIC = Path(__file__).resolve().parent / "static"
MAX_BODY = 4096


class Handler(BaseHTTPRequestHandler):
    server_version = "CashflowGuardian/0.9"

    def _allowed(self):
        host = self.headers.get('Host', '')
        allowed = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
        origin = self.headers.get('Origin')
        if host not in allowed or (origin is not None and origin != 'http://' + host):
            self._send({'error': 'Untrusted origin or host'}, 403)
            return False
        if self.headers.get('Sec-Fetch-Site') == 'cross-site':
            self._send({'error': 'Cross-site access denied'}, 403)
            return False
        return True

    def _send(self, payload, status=200):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'")
        self.end_headers()
        self.wfile.write(data)

    def _static(self, filename, content_type):
        try:
            data = (STATIC / filename).read_bytes()
        except FileNotFoundError:
            self._send({"error": "Not found"}, status=404)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(data)

    @staticmethod
    def _report(source):
        if source == "demo":
            return score_invoices(demo_invoices())
        if source == "sandbox":
            return score_invoices(get_invoices())
        raise ValueError("source must be demo or sandbox")

    def do_GET(self):
        if not self._allowed():
            return
        path = urlsplit(self.path)
        if path.path in ("/", "/index.html"):
            return self._static("index.html", "text/html; charset=utf-8")
        if path.path == "/style.css":
            return self._static("style.css", "text/css; charset=utf-8")
        if path.path == "/i18n.js":
            return self._static("i18n.js", "application/javascript; charset=utf-8")
        if path.path == "/settings.js":
            return self._static("settings.js", "application/javascript; charset=utf-8")
        if path.path == "/workbench.js":
            return self._static("workbench.js", "application/javascript; charset=utf-8")
        if path.path == "/app.js":
            return self._static("app.js", "application/javascript; charset=utf-8")
        vendor_assets = {
            "/vendor/ag-grid/ag-grid-community.min.js": ("vendor/ag-grid/ag-grid-community.min.js", "application/javascript; charset=utf-8"),
            "/vendor/ag-grid/styles/ag-grid.min.css": ("vendor/ag-grid/styles/ag-grid.min.css", "text/css; charset=utf-8"),
            "/vendor/ag-grid/styles/ag-theme-quartz.min.css": ("vendor/ag-grid/styles/ag-theme-quartz.min.css", "text/css; charset=utf-8"),
        }
        if path.path in vendor_assets:
            return self._static(*vendor_assets[path.path])
        if path.path == "/api/status":
            return self._send({"sandbox_configured": sandbox_configured(), "mode": "read-only", "environment": "sandbox", "ai": "TF-IDF and IsolationForest (local)", "external_ai_configured": is_configured(), "external_ai_scope": "synthetic-demo-only"})
        if path.path == "/api/analyze":
            source = parse_qs(path.query).get("source", ["demo"])[0]
            try:
                report = self._report(source)
                report["source"] = source
                return self._send(report)
            except ValueError as exc:
                return self._send({"error": str(exc)}, status=400)
            except PayPalError as exc:
                return self._send({"error": str(exc)}, status=502)
        if path.path.startswith("/api/invoices/"):
            invoice_id = path.path.removeprefix("/api/invoices/")
            if parse_qs(path.query).get("source", ["sandbox"])[0] != "sandbox":
                return self._send({"error": "Invoice details are available only for PayPal Sandbox"}, status=400)
            try:
                return self._send(get_invoice_detail(invoice_id))
            except PayPalError as exc:
                status = 400 if "Invalid invoice ID" in str(exc) else 502
                return self._send({"error": str(exc)}, status=status)
        self._send({"error": "Not found"}, status=404)

    def do_POST(self):
        if not self._allowed():
            return
        path = urlsplit(self.path).path
        if path not in ('/api/ask', '/api/import', '/api/ai/ask'):
            return self._send({"error": "Not found"}, status=404)
        if self.headers.get('Content-Type', '').split(';')[0].strip().lower() != 'application/json':
            return self._send({'error': 'JSON required'}, 415)
        try:
            size = int(self.headers.get("Content-Length", "0"))
            limit = 2_000_000 if path == '/api/import' else MAX_BODY
            if size <= 0 or size > limit:
                return self._send({"error": "Request body size outside allowed bounds"}, status=413)
            self.connection.settimeout(10)
            payload = json.loads(self.rfile.read(size))
            if path == '/api/ai/ask':
                # This route accepts only a question; invoice data/source selectors are rejected.
                if set(payload) != {"question"}:
                    return self._send({"error": "Only a question is accepted by the synthetic-data AI route"}, status=400)
                answer = ask_synthetic(payload.get("question", ""))
                return self._send({"answer": answer, "source": "synthetic-demo", "external": True})
            if path == '/api/import':
                result = score_invoices(validate_invoices(payload))
                result['source'] = 'import'
                return self._send(result)
            question = payload.get("question", "")
            source = payload.get("source", "demo")
            if not isinstance(question, str) or len(question) > 500:
                return self._send({"error": "Invalid question"}, status=400)
            result = self._report(source)
            return self._send({"answer": answer_question(result, question)})
        except (ValueError, json.JSONDecodeError, AttributeError, TypeError, TimeoutError):
            return self._send({"error": "Invalid request"}, status=400)
        except LlmUnavailable as exc:
            return self._send({"error": str(exc)}, status=503)
        except PayPalError as exc:
            return self._send({"error": str(exc)}, status=502)

    def log_message(self, fmt, *args):
        # Request paths can contain user queries; avoid persisting them to logs.
        if self.path == "/api/status":
            return
        super().log_message("%s %s", self.command, self.path.split("?")[0])


def start(host="127.0.0.1", port=8765):
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"Cashflow Guardian running at http://{host}:{port} — synthetic demo by default")
    print("Sandbox access is read-only. Never paste API secrets into the browser or chat.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PayPal AI Hackathon: Cashflow Guardian demo")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    start(port=args.port)
