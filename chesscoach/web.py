"""Telefon dostu web arayüzü (stdlib — ek bağımlılık yok).

Çalıştır:  python -m chesscoach.web
Sonra telefondan aynı Wi-Fi'da:  http://<bilgisayar-ip>:8000

Ekran görüntüsü yükle → sıra kimde seç → en iyi hamle + anlatım gelir.
Görüntüden FEN için GEMINI_API_KEY gerekir; FEN'i elle de yapıştırabilirsin.
"""
from __future__ import annotations

import html
import io
import json
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .engine import ChessEngine
from .explain import describe

PAGE = """<!doctype html><html lang=tr><head>
<meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Satranç Koçu</title>
<style>
 body{{font-family:system-ui,sans-serif;max-width:680px;margin:0 auto;padding:16px;background:#111;color:#eee}}
 h1{{font-size:1.3rem}} label{{display:block;margin:12px 0 4px}}
 input,select,button,textarea{{font-size:1rem;width:100%;padding:10px;box-sizing:border-box;
   border-radius:8px;border:1px solid #444;background:#1c1c1c;color:#eee}}
 button{{background:#2d6cdf;border:0;margin-top:14px;font-weight:600}}
 pre{{white-space:pre-wrap;background:#000;padding:14px;border-radius:8px;line-height:1.5}}
 .hint{{color:#888;font-size:.85rem}}
</style></head><body>
<h1>♟️ Satranç Koçu</h1>
<form method=post enctype=multipart/form-data action=/analyze>
 <label>Tahta ekran görüntüsü <span class=hint>(Gemini anahtarı gerekir)</span></label>
 <input type=file name=image accept=image/*>
 <label>…veya FEN'i elle yapıştır</label>
 <input type=text name=fen placeholder="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1">
 <label>Sıra kimde?</label>
 <select name=side><option value=w>Beyaz</option><option value=b>Siyah</option></select>
 <label>Derinlik <span class=hint>(yüksek = daha güçlü, daha yavaş)</span></label>
 <input type=number name=depth value=18 min=6 max=30>
 <button type=submit>Analiz Et</button>
</form>
{result}
</body></html>"""


def _parse_multipart(body: bytes, boundary: bytes) -> dict:
    """Çok küçük bir multipart/form-data ayrıştırıcı (stdlib yeterli değil)."""
    fields = {}
    for part in body.split(b"--" + boundary):
        if b"\r\n\r\n" not in part:
            continue
        head, data = part.split(b"\r\n\r\n", 1)
        data = data.rstrip(b"\r\n")
        head_s = head.decode("utf-8", "ignore")
        if 'name="' not in head_s:
            continue
        name = head_s.split('name="', 1)[1].split('"', 1)[0]
        if "filename=" in head_s:
            fields[name] = ("file", data)
        else:
            fields[name] = ("text", data.decode("utf-8", "ignore").strip())
    return fields


class Handler(BaseHTTPRequestHandler):
    engine = None

    def _send(self, body: str, code: int = 200):
        b = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path != "/":
            self._send("yok", 404)
            return
        self._send(PAGE.format(result=""))

    def do_POST(self):
        if self.path != "/analyze":
            self._send("yok", 404)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        ctype = self.headers.get("Content-Type", "")
        boundary = ctype.split("boundary=")[-1].encode() if "boundary=" in ctype else b""
        fields = _parse_multipart(body, boundary) if boundary else {}

        fen = (fields.get("fen") or ("text", ""))[1]
        side = (fields.get("side") or ("text", "w"))[1]
        try:
            depth = int((fields.get("depth") or ("text", "18"))[1])
        except ValueError:
            depth = 18

        try:
            img = fields.get("image")
            if img and img[0] == "file" and img[1]:
                from .vision import image_to_fen
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
                    tf.write(img[1])
                    tmp = tf.name
                fen = image_to_fen(tmp, side_to_move=side)
            if not fen:
                raise ValueError("Görüntü ya da FEN ver.")
            analysis = (self.engine or ChessEngine()).analyse(fen, depth=depth)
            out = f"📷/⌨️  FEN: {fen}\n\n" + describe(analysis)
        except Exception as e:
            out = f"❌ Hata: {e}"

        self._send(PAGE.format(result=f"<pre>{html.escape(out)}</pre>"))

    def log_message(self, *a):  # sessiz
        pass


def serve(host: str = "0.0.0.0", port: int = 8000):
    Handler.engine = ChessEngine()
    srv = ThreadingHTTPServer((host, port), Handler)
    print(f"♟️  Satranç Koçu çalışıyor → http://{host}:{port}")
    print("   Telefondan aynı ağda bilgisayarının IP'siyle aç (örn. http://192.168.1.20:8000)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nKapatılıyor…")


if __name__ == "__main__":
    serve()
