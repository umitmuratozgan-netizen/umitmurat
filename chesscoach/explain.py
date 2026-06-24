"""Analiz çıktısını insanca Türkçe anlatıma çevirir.

Tamamen çevrimdışı, kural tabanlı — motor verisinden üretilir. İstenirse
LLM (Gemini/Claude) ile daha akıcı hale getirilebilir (bkz. llm_polish).
"""
from __future__ import annotations

from .engine import Analysis


def eval_to_words(a: Analysis) -> str:
    if a.mate_in is not None:
        if a.mate_in > 0:
            return f"♛ {a.mate_in} hamlede MAT var — zorla kazanıyorsun."
        return f"⚠️ Rakipte {abs(a.mate_in)} hamlede mat tehdidi — savunmadasın."
    cp = a.score_cp or 0
    pawns = cp / 100
    if cp >= 500:
        tag = "kazanan üstünlük (neredeyse bitti)"
    elif cp >= 200:
        tag = "belirgin üstünsün"
    elif cp >= 80:
        tag = "hafif üstünsün"
    elif cp > -80:
        tag = "pozisyon yaklaşık eşit"
    elif cp > -200:
        tag = "hafif gerisin"
    elif cp > -500:
        tag = "belirgin gerisin"
    else:
        tag = "kaybeden pozisyon — dikkatli savun"
    return f"Değerlendirme: {pawns:+.2f} ({tag})."


def describe(a: Analysis) -> str:
    lines = []
    side = "Beyaz" if a.turn == "white" else "Siyah"
    lines.append(f"♟️  Sıra: {side}  |  Derinlik: {a.depth}")
    lines.append(eval_to_words(a))
    lines.append("")
    lines.append(f"➡️  EN İYİ HAMLE:  {a.best_move_san}   ({a.best_move_uci})")

    if a.pv_san:
        lines.append(f"    Devamı (ana varyant): {' '.join(a.pv_san)}")

    if a.opponent_threat_san:
        lines.append(f"⚔️  Rakibin asıl tehdidi: {a.opponent_threat_san} "
                     f"(sen hamle yapmazsan bunu oynar).")

    if a.hanging:
        lines.append(f"🩸  Asılı (bedava) taşların: {', '.join(a.hanging)} — koru veya kaç.")

    lines.append("")
    lines.append(_plan_hint(a))
    return "\n".join(lines)


def _plan_hint(a: Analysis) -> str:
    san = a.best_move_san
    if "#" in san:
        return "💡 Plan: Mat hamlesi — direkt oyna."
    if "+" in san:
        return "💡 Plan: Şah çekerek inisiyatifi al; rakibin cevabı zorunlu."
    if "x" in san:
        return "💡 Plan: Taş kazanımı/değişim — materyal dengesini lehine çevir."
    if san[:1] in ("O", "0"):
        return "💡 Plan: Rok — şahı güvene al, kaleyi oyuna sok."
    cp = a.score_cp or 0
    if cp < -150:
        return "💡 Plan: Savunmadasın — taşları koru, rakibin saldırısını yavaşlat, sadeleş."
    return "💡 Plan: Üstünlüğü artır — taş geliştir, merkezi tut, zayıf kareleri hedefle."


# ---- isteğe bağlı LLM cilası (Gemini/Claude) ----------------------------------

def llm_polish(a: Analysis, provider: str = "gemini") -> str:
    """Motor analizini LLM'e verip daha akıcı bir koç anlatımı ürettirir.

    LLM'e HAMLE SORDURMUYORUZ — sadece Stockfish'in bulduğu hamleyi açıklatıyoruz.
    Anahtar yoksa kural tabanlı describe()'a düşer.
    """
    facts = describe(a)
    prompt = (
        "Sen bir satranç koçusun. Aşağıda Stockfish motorunun bir pozisyon için "
        "verdiği KESİN analiz var. Bu hamleyi DEĞİŞTİRME, sadece bir öğrenciye "
        "anlatır gibi 3-4 cümleyle Türkçe açıkla: neden bu hamle, rakip ne "
        "planlıyor, hangi karelere dikkat etmeli.\n\n"
        f"FEN: {a.fen}\n{facts}"
    )
    try:
        if provider == "gemini":
            return _gemini(prompt) or facts
        return facts
    except Exception:
        return facts


def _gemini(prompt: str) -> str | None:
    import os
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    import urllib.request, json
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           f"gemini-1.5-flash:generateContent?key={key}")
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
