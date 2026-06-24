# Satranç Koçu — bulut için Docker imajı
# Stockfish motorunu + Python kütüphanesini kurar, web sunucusunu başlatır.
FROM python:3.12-slim

# Stockfish motoru (apt deposundan)
RUN apt-get update \
    && apt-get install -y --no-install-recommends stockfish \
    && rm -rf /var/lib/apt/lists/*

# Stockfish'in apt'taki yolu /usr/games/stockfish — kod bunu otomatik bulur,
# yine de açıkça verelim.
ENV STOCKFISH_PATH=/usr/games/stockfish

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY chesscoach ./chesscoach

# Bulut host'u PORT ortam değişkenini verir; web.py bunu okur.
EXPOSE 8000
CMD ["python", "-m", "chesscoach.web"]
