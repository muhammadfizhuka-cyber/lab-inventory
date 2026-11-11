"""Lab Inventory REST API - Python standard library only (tanpa framework)."""
import json
import os
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

DATA_DIR = os.environ.get("DATA_DIR", "/var/lib/backend_data")
DATA_FILE = os.path.join(DATA_DIR, "inventory.json")
PORT = int(os.environ.get("PORT", "5000"))
VALID_STATUS = {"Tersedia", "Dipinjam", "Rusak"}
lock = threading.Lock()


def load_items():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_items(items):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    os.replace(tmp, DATA_FILE)  # atomic write


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, {})

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            return self._send(200, {"status": "ok"})
        if path == "/inventory":
            with lock:
                items = load_items()
            return self._send(200, {"total": len(items), "items": items})
        self._send(404, {"error": "Endpoint tidak ditemukan"})

    def do_POST(self):
        if urlparse(self.path).path != "/inventory":
            return self._send(404, {"error": "Endpoint tidak ditemukan"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(data, dict):
                raise ValueError
        except (ValueError, json.JSONDecodeError):
            return self._send(400, {"error": "Body harus berupa JSON object yang valid"})

        name = str(data.get("name", "")).strip()
        category = str(data.get("category", "")).strip()
        status = str(data.get("status", "Tersedia")).strip()
        try:
            quantity = int(data.get("quantity", 1))
        except (TypeError, ValueError):
            return self._send(400, {"error": "quantity harus berupa angka"})

        if not name:
            return self._send(400, {"error": "Field 'name' wajib diisi"})
        if quantity < 1:
            return self._send(400, {"error": "quantity minimal 1"})
        if status not in VALID_STATUS:
            return self._send(400, {"error": "status harus salah satu dari: " + ", ".join(sorted(VALID_STATUS))})

        item = {
            "name": name,
            "category": category or "Lainnya",
            "quantity": quantity,
            "status": status,
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        with lock:
            items = load_items()
            items.append(item)
            save_items(items)
        self._send(201, {"message": "Alat ditambahkan", "item": item})

    def do_DELETE(self):
        parsed = urlparse(self.path)
        if parsed.path != "/inventory":
            return self._send(404, {"error": "Endpoint tidak ditemukan"})
        raw = parse_qs(parsed.query).get("index", [None])[0]
        if raw is None:
            return self._send(400, {"error": "Query param 'index' wajib diisi"})
        try:
            index = int(raw)
        except ValueError:
            return self._send(400, {"error": "index harus berupa angka"})
        with lock:
            items = load_items()
            if index < 0 or index >= len(items):
                return self._send(404, {"error": "Data dengan index tersebut tidak ada"})
            removed = items.pop(index)
            save_items(items)
        self._send(200, {"message": "Alat dihapus", "item": removed})

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args), flush=True)


if __name__ == "__main__":
    print(f"Backend jalan di port {PORT}, data di {DATA_FILE}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
