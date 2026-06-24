"""Telefon ekran görüntüsü → FEN dönüşümü.

Tahtanın fotoğrafını/screenshot'ını alıp tahta dizilimini FEN'e çevirir.
Varsayılan: Google Gemini Vision (ücretsiz katman mevcut). İstersen Claude
Vision'a da eklenebilir.

Kurulum:  export GEMINI_API_KEY="..."   (https://aistudio.google.com/apikey)
"""
from __future__ import annotations

import base64
import json
import os
import re
import urllib.request

import chess

_PROMPT = (
    "Bu bir satranç tahtası görüntüsü. Tahtadaki dizilimi oku ve SADECE FEN "
    "dizgisinin taş yerleşimi alanını döndür (başka açıklama yazma). "
    "Standart FEN gösterimi: büyük harf=beyaz, küçük harf=siyah, sayı=boş kare, "
    "satırlar 8. yataydan 1.'e '/' ile ayrılır. "
    "Mümkünse sıranın kimde olduğunu da 'w' veya 'b' olarak ikinci alanda ver. "
    "Örnek çıktı: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w"
)


def image_to_fen(image_path: str, side_to_move: str | None = None,
                 provider: str = "gemini") -> str:
    """Görüntüden tam FEN üretir. side_to_move verilirse ('w'/'b') onu kullanır."""
    if provider == "gemini":
        raw = _gemini_vision(image_path)
    else:
        raise ValueError(f"Bilinmeyen vision sağlayıcı: {provider}")

    placement, detected_turn = _parse(raw)
    turn = side_to_move or detected_turn or "w"
    fen = f"{placement} {turn} - - 0 1"
    chess.Board(fen)  # doğrula — geçersizse ValueError
    return fen


def _parse(raw: str) -> tuple[str, str | None]:
    """LLM çıktısından taş yerleşimini ve (varsa) sıra bilgisini ayıklar."""
    raw = raw.strip().strip("`").strip()
    # 8 alanlı satır + opsiyonel ' w/b'
    m = re.search(r"([prnbqkPRNBQK1-8]+(?:/[prnbqkPRNBQK1-8]+){7})(?:\s+([wb]))?", raw)
    if not m:
        raise ValueError(f"Görüntüden FEN okunamadı. Model çıktısı: {raw[:120]!r}")
    return m.group(1), m.group(2)


def _gemini_vision(image_path: str) -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY ayarlı değil. https://aistudio.google.com/apikey "
            "adresinden ücretsiz anahtar al ve 'export GEMINI_API_KEY=...' yap."
        )
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    mime = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"

    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           f"gemini-1.5-flash:generateContent?key={key}")
    body = json.dumps({
        "contents": [{"parts": [
            {"text": _PROMPT},
            {"inline_data": {"mime_type": mime, "data": b64}},
        ]}]
    }).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    return data["candidates"][0]["content"]["parts"][0]["text"]
