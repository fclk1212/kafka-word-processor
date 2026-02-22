"""
Word filtering logic.

Given a sentence (or list of sentences) returns only the words that
meet the minimum character-length requirement.

Rules applied:
  1. Tokenise by Unicode word boundaries (letters only).
  2. Lowercase – deduplication and downstream consumers will receive
     normalised tokens.
  3. Keep only tokens whose length >= min_length.
"""
import re
import logging
from typing import List

logger = logging.getLogger(__name__)

# Matches sequences of Unicode letters only (no digits, no punctuation).
_WORD_PATTERN = re.compile(r"\b[A-Za-zÀ-ÿ]+\b")


class WordFilter:
    """Extracts words of at least *min_length* characters from text."""

    def __init__(self, min_length: int = 5):
        if min_length < 1:
            raise ValueError("min_length must be >= 1")
        self.min_length = min_length

    # ── Public interface ─────────────────────────────────────────────────────

    def filter_sentence(self, sentence: str) -> List[str]:
        """Return qualifying words from a single sentence."""
        tokens = _WORD_PATTERN.findall(sentence)
        result = [t.lower() for t in tokens if len(t) >= self.min_length]
        logger.debug(
            "sentence filtered: %d/%d tokens kept", len(result), len(tokens)
        )
        return result

    def filter_sentences(self, sentences: List[str]) -> List[str]:
        """Return a flat list of qualifying words across all sentences."""
        result: List[str] = []
        for sentence in sentences:
            result.extend(self.filter_sentence(sentence))
        return result
