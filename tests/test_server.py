import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from server import Handler


def test_http_routes():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=httpd.serve_forever, daemon=True)
    worker.start()
    base = f"http://127.0.0.1:{httpd.server_port}"
    try:
        with urlopen(base + "/api/status", timeout=10) as response:
            config = json.load(response)
            assert config["environment"] == "sandbox"
            assert config["mode"] == "read-only"
        with urlopen(base + "/api/analyze?source=demo", timeout=10) as response:
            payload = json.load(response)
            assert payload["summary"]["invoice_count"] == 15
        with urlopen(base + "/settings.js", timeout=10) as response:
            assert "cgBrowserLocale" in response.read().decode()
        request = Request(base + "/api/ask", data=json.dumps({"question": "Find duplicates", "source": "demo"}).encode(), headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=10) as response:
            message = json.load(response)
            assert "INV-1024" in message["answer"]
        with urlopen(base + "/", timeout=10) as response:
            html = response.read().decode()
            assert "cashflow guardian" in html.lower()
            assert "invoiceGrid" in html
        try:
            urlopen(base + "/api/analyze?source=production", timeout=10)
        except HTTPError as exc:
            assert exc.code == 400
        else:
            raise AssertionError("Production connection should be disabled")
    finally:
        httpd.shutdown()
        worker.join(timeout=5)
        httpd.server_close()
