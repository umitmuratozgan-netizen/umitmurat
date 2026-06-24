# ♟️ Satranç Koçu (chesscoach)

Bir satranç pozisyonunun **ekran görüntüsünü** ver → en iyi hamleyi, değerlendirmeyi,
rakibin tehdidini ve **insanca Türkçe açıklamayı** al.

> **Önemli — adil oyun:** Bu bir **antrenman ve analiz** aracıdır. Canlı bir rakibe
> karşı gizlice kullanmak (Chess.com / Lichess / turnuva) hiledir ve hesabını
> kapattırır. Kendi oyunlarını çalışmak, pozisyon analizi ve gelişmek için kullan.

## Neden bu mimari?

LLM'ler (Gemini/Claude) satrançta **hamle seçmede zayıftır** — illegal hamle önerir,
taktik kaçırır. Bu yüzden iş bölümü:

| Parça | Görev | Araç |
|------|-------|------|
| 🧠 Hamle gücü | en iyi hamle + değerlendirme | **Stockfish 16** (ücretsiz, en güçlü) |
| 👁️ Görüntü→FEN | ekran görüntüsünü pozisyona çevir | **Gemini Vision** (ücretsiz katman) |
| 💬 Anlatım | "neden bu hamle, rakip ne planlıyor" | kural tabanlı + isteğe bağlı LLM |

Hamleyi **her zaman Stockfish** belirler; LLM sadece açıklar.

## Kurulum

```bash
# 1) Stockfish motoru
sudo apt-get install stockfish        # veya stockfishchess.org/download

# 2) Python kütüphanesi
pip install -r requirements.txt

# 3) (görüntüden FEN istiyorsan) ücretsiz Gemini anahtarı
#    https://aistudio.google.com/apikey
export GEMINI_API_KEY="senin-anahtarın"
```

## Kullanım

### Komut satırı
```bash
# FEN ile (anahtar gerekmez)
python -m chesscoach --fen "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 4 4"

# Ekran görüntüsü ile (Gemini anahtarı gerekir)
python -m chesscoach --image tahta.png --side w

# Gemini ile daha akıcı koç anlatımı
python -m chesscoach --image tahta.png --side w --llm
```

### Telefon için web arayüzü
```bash
python -m chesscoach.web
```
Sonra telefonundan **aynı Wi-Fi ağında** bilgisayarının IP'siyle aç:
`http://192.168.1.x:8000` → screenshot yükle → analiz al.

## Örnek çıktı
```
♟️  Sıra: Beyaz  |  Derinlik: 18
♛ 1 hamlede MAT var — zorla kazanıyorsun.

➡️  EN İYİ HAMLE:  Qxf7#   (f3f7)
    Devamı (ana varyant): Qxf7#
⚔️  Rakibin asıl tehdidi: Nf6
💡 Plan: Mat hamlesi — direkt oyna.
```

## Yol haritası (sıradaki adımlar)
- [ ] Claude Vision'ı ikinci görüntü sağlayıcı olarak ekle
- [ ] Çoklu aday hamle (multipv) + kıyas
- [ ] Açılış adı tanıma
- [ ] Görüntü→FEN'i yerel CV modeliyle (anahtarsız) yapma seçeneği
