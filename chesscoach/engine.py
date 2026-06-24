"""Stockfish tabanlı analiz çekirdeği.

LLM'ler satrançta zayıftır (illegal hamle, taktik kaçırma). Bu yüzden hamle
gücünün TAMAMI Stockfish'ten gelir. LLM yalnızca açıklama/anlatım için kullanılır.
"""
from __future__ import annotations

import logging
import os
import shutil

logging.getLogger("chess.engine").setLevel(logging.ERROR)  # null-move uyarısını sustur
from dataclasses import dataclass, field
from typing import Optional

import chess
import chess.engine


def find_stockfish() -> str:
    """Sistemde Stockfish çalıştırılabilirini bulur."""
    env = os.environ.get("STOCKFISH_PATH")
    if env and os.path.exists(env):
        return env
    for name in ("stockfish", "/usr/games/stockfish", "/usr/local/bin/stockfish"):
        path = shutil.which(name) or (name if os.path.exists(name) else None)
        if path:
            return path
    raise FileNotFoundError(
        "Stockfish bulunamadı. 'apt-get install stockfish' ile kur "
        "veya STOCKFISH_PATH ortam değişkenini ayarla."
    )


@dataclass
class Analysis:
    fen: str
    turn: str                       # "white" / "black" — sırası gelen taraf
    best_move_uci: str
    best_move_san: str
    score_cp: Optional[int]         # taşı süren tarafın gözünden centipawn (+ iyi)
    mate_in: Optional[int]          # mat varsa kaç hamlede (+ lehine, - aleyhine)
    pv_san: list[str] = field(default_factory=list)   # önerilen varyant
    opponent_threat_san: Optional[str] = None         # rakibin asıl tehdidi
    hanging: list[str] = field(default_factory=list)  # bedava (asılı) taşlar
    depth: int = 0


class ChessEngine:
    def __init__(self, path: Optional[str] = None, threads: int = 2, hash_mb: int = 128):
        self.path = path or find_stockfish()
        self._opts = {"Threads": threads, "Hash": hash_mb}

    def _open(self) -> chess.engine.SimpleEngine:
        eng = chess.engine.SimpleEngine.popen_uci(self.path)
        try:
            eng.configure(self._opts)
        except Exception:
            pass
        return eng

    def analyse(self, fen: str, depth: int = 18, movetime: Optional[float] = None) -> Analysis:
        board = chess.Board(fen)  # geçersiz FEN burada ValueError fırlatır
        limit = chess.engine.Limit(time=movetime) if movetime else chess.engine.Limit(depth=depth)

        eng = self._open()
        try:
            info = eng.analyse(board, limit)
            pv = info.get("pv", [])
            score = info["score"].pov(board.turn)

            best = pv[0] if pv else None
            best_san = board.san(best) if best else "(hamle yok)"

            # rakibin asıl tehdidi: biz pas geçseydik (null move) rakip ne oynardı?
            opp_threat = self._opponent_threat(board, eng, limit)

            return Analysis(
                fen=fen,
                turn="white" if board.turn == chess.WHITE else "black",
                best_move_uci=best.uci() if best else "",
                best_move_san=best_san,
                score_cp=score.score(),
                mate_in=score.mate(),
                pv_san=self._pv_to_san(board, pv),
                opponent_threat_san=opp_threat,
                hanging=self._hanging_pieces(board),
                depth=info.get("depth", 0),
            )
        finally:
            eng.quit()

    @staticmethod
    def _pv_to_san(board: chess.Board, pv: list[chess.Move], n: int = 6) -> list[str]:
        out, b = [], board.copy()
        for mv in pv[:n]:
            try:
                out.append(b.san(mv))
                b.push(mv)
            except Exception:
                break
        return out

    def _opponent_threat(self, board, eng, limit) -> Optional[str]:
        """Sıra bizdeyken 'pas geçsek' rakip en güçlü ne yapardı? = asıl tehdit."""
        if board.is_check():
            return None  # şah altındayken null move geçersiz
        b = board.copy()
        try:
            b.push(chess.Move.null())
            info = eng.analyse(b, chess.engine.Limit(depth=min(12, getattr(limit, "depth", 12) or 12)))
            pv = info.get("pv", [])
            if pv:
                return b.san(pv[0])
        except Exception:
            return None
        return None

    @staticmethod
    def _hanging_pieces(board: chess.Board) -> list[str]:
        """Sırası gelen tarafın, savunmasız şekilde saldırı altında olan taşları."""
        out = []
        us = board.turn
        for sq, piece in board.piece_map().items():
            if piece.color != us or piece.piece_type == chess.KING:
                continue
            attackers = board.attackers(not us, sq)
            if attackers and not board.attackers(us, sq):
                out.append(f"{piece.symbol().upper()}{chess.square_name(sq)}")
        return out
