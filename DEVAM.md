# 📌 DEVAM NOTU — Satranç Koçu (evde buradan devam et)

Bu dosya, iş bilgisayarında başlanan çalışmanın özeti ve evde yapılacakların listesidir.
**Tüm kod GitHub'da kayıtlı, hiçbir şey kaybolmadı.** Branch: `claude/fervent-knuth-nqdkc6`

---

## Bu proje ne?
Satranç pozisyonunun **ekran görüntüsünü** ver → en iyi hamle + değerlendirme +
rakibin planı + Türkçe açıklama al. Telefondan kullanmak için.

**Mimari:** Hamleyi her zaman **Stockfish** (en güçlü motor) seçer. **Gemini Vision**
ekran görüntüsünü FEN'e çevirir. LLM sadece açıklama yapar (hamle seçmez — çünkü
LLM'ler satrançta zayıftır).

> ⚠️ **Adil oyun:** Bu bir ANTRENMAN/ANALİZ aracı. Canlı rakibe karşı gizli kullanmak
> hiledir, hesabını kapattırır. Kendi oyunlarını çalışmak için kullan.

---

## ✅ Şimdiye kadar yapılanlar
- Uygulama yazıldı, test edildi, çalışıyor (CLI + telefon web arayüzü)
- Stockfish 16 + python-chess ile mat/analiz doğrulandı
- Bulut için Docker + Render ayarları hazır, GitHub'a push'landı
- İş bilgisayarında lokal test başarılı oldu (mat pozisyonu doğru bulundu)

## ⏳ Evde kalan TEK iş: bulut'a deploy (3 adım, sadece tarayıcı)

### Adım 1 — Ücretsiz Gemini anahtarı
- https://aistudio.google.com/apikey → "Create API key" → `AIza...` anahtarını kopyala

### Adım 2 — Render'a deploy (kart gerekmez)
1. https://render.com → GitHub ile giriş yap
2. `New +` → `Blueprint`
3. Repo: `umitmuratozgan-netizen/umitmurat` → Connect (render.yaml otomatik okunur)
4. İki ortam değişkenini gir:
   - `GEMINI_API_KEY` = Adım 1'deki anahtar
   - `CHESS_TOKEN` = kendin uydur (örn. `umit2026gizli`) — linki başkası açamasın diye
5. `Apply` → build ~3-5 dk (Stockfish dahil kurulur)

### Adım 3 — Telefonda aç
- Render bir link verir: `https://satranc-kocu.onrender.com`
- Telefonda token ekleyerek aç: `https://satranc-kocu.onrender.com/?token=umit2026gizli`
- Linki telefon ana ekranına kısayol ekle → uygulama gibi açılır
- Kullanım: ekran görüntüsü yükle + sıra kimde seç + Analiz Et

> ⏳ Ücretsiz katman 15 dk kullanılmazsa uyur; ilk açılış ~50 sn sürer, sonra hızlı. Normaldir.

---

## Alternatif: evde lokal çalıştırma (bulut yerine, sadece ev Wi-Fi'da)
```powershell
# 1) Kodu indir: GitHub → branch claude/fervent-knuth-nqdkc6 → Code → Download ZIP → çıkar
# 2) chesscoach klasörünü gören klasöre gir:
cd <proje-klasörü>
pip install chess
# 3) Stockfish indir (https://stockfishchess.org/download), exe yolunu ayarla:
$env:STOCKFISH_PATH="C:\stockfish\...\stockfish-windows-x86-64.exe"
# 4) Çalıştır:
python -m chesscoach.web
# 5) Tarayıcı: http://localhost:8000 ; telefon (aynı Wi-Fi): http://<pc-ip>:8000
```
Not: Lokal yöntem sadece PC ile aynı ağdayken çalışır; dışarıdan erişim için bulut (Render) gerekir.

---

## Sıradaki olası geliştirmeler (istersen)
- [ ] Claude Vision'ı ikinci görüntü okuyucu olarak ekle
- [ ] Çoklu aday hamle (en iyi 3 hamle kıyas)
- [ ] Açılış adı tanıma
- [ ] Anahtarsız (yerel görüntü işleme) FEN okuma
