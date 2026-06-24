"""chesscoach — Stockfish destekli satranç koçu.

Akış: ekran görüntüsü → FEN (vision) → Stockfish analizi → Türkçe anlatım.
Hamle gücü Stockfish'ten; LLM yalnızca açıklama için kullanılır.
"""
from .engine import ChessEngine, Analysis
from .explain import describe, llm_polish

__all__ = ["ChessEngine", "Analysis", "describe", "llm_polish"]
__version__ = "0.1.0"
