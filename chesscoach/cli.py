"""Komut satırı arayüzü.

Örnekler:
  python -m chesscoach --fen "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 4 4"
  python -m chesscoach --image ekran.png --side w
  python -m chesscoach --image ekran.png --llm           # Gemini ile akıcı anlatım
"""
from __future__ import annotations

import argparse
import sys

from .engine import ChessEngine
from .explain import describe, llm_polish


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="chesscoach", description="Satranç koçu (Stockfish + Vision)")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--fen", help="Analiz edilecek FEN dizgisi")
    src.add_argument("--image", help="Tahta ekran görüntüsü (png/jpg)")
    p.add_argument("--side", choices=["w", "b"], help="Görüntüde sıra kimde (varsayılan: modelden/oku)")
    p.add_argument("--depth", type=int, default=18, help="Stockfish arama derinliği (varsayılan 18)")
    p.add_argument("--movetime", type=float, help="Derinlik yerine saniye cinsinden süre")
    p.add_argument("--llm", action="store_true", help="Gemini ile akıcı koç anlatımı üret")
    args = p.parse_args(argv)

    if args.image:
        from .vision import image_to_fen
        try:
            fen = image_to_fen(args.image, side_to_move=args.side)
            print(f"📷 Okunan FEN: {fen}\n")
        except Exception as e:
            print(f"❌ Görüntü okunamadı: {e}", file=sys.stderr)
            return 2
    else:
        fen = args.fen

    try:
        engine = ChessEngine()
        analysis = engine.analyse(fen, depth=args.depth, movetime=args.movetime)
    except Exception as e:
        print(f"❌ Analiz hatası: {e}", file=sys.stderr)
        return 2

    print(llm_polish(analysis) if args.llm else describe(analysis))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
