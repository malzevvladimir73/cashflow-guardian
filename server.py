"""Zero-dependency HTTP server for Cashflow Guardian (localhost only)."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from demo_data import demo_invoices
from intelligence import answer_question, score_invoices
from paypal_client import PayPalError, get_invoices, sandbox_configured

STATIC = Path(__file__).resolve().parent / "static"
MAX_BODY = 4096


class Handler(BaseHTTPRequestHandler):
    server_version = "CashflowGuardian/0.1"

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
        path = urlsplit(self.path)
        if path.path in ("/", "/index.html"):
            return self._static("index.html", "text/html; charset=utf-8")
        if path.path == "/style.css":
            return self._static("style.css", "text/css; charset=utf-8")
        if path.path == "/i18n.js":
            return self._static("i18n.js", "application/javascript; charset=utf-8")
        if path.path == "/settings.js":
            return self._static("settings.js", "application/javascript; charset=utf-8")
        if path.path == "/app.js":
            return self._static("app.js", "application/javascript; charset=utf-8")
        if path.path == "/api/status":
            return self._send({"sandbox_configured": sandbox_configured(), "mode": "read-only", "environment": "sandbox", "ai": "TF-IDF and IsolationForest (local)"})
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
        self._send({"error": "Not found"}, status=404)

    def do_POST(self):
        if urlsplit(self.path).path != "/api/ask":
            return self._send({"error": "Not found"}, status=404)
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > MAX_BODY:
                return self._send({"error": "Request size must be between 1 and 4096 bytes"}, status=413)
            payload = json.loads(self.rfile.read(size))
            question = payload.get("question", "")
            source = payload.get("source", "demo")
            if not isinstance(question, str) or len(question) > 500:
                return self._send({"error": "Invalid question"}, status=400)
            result = self._report(source)
            return self._send({"answer": answer_question(result, question)})
        except (ValueError, json.JSONDecodeError, AttributeError):
            return self._send({"error": "Invalid request"}, status=400)
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
