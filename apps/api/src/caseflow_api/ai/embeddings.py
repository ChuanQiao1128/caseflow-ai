from __future__ import annotations

import math
import re
from collections.abc import Iterable, Sequence
from hashlib import sha256
from typing import Final

EMBEDDING_DIMENSION: Final[int] = 1536
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def _normalize_text(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _hash_to_index(value: str) -> int:
    digest = sha256(value.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False) % EMBEDDING_DIMENSION


def _hash_to_sign(value: str) -> float:
    digest = sha256((value + "::sign").encode("utf-8")).digest()
    return 1.0 if digest[0] % 2 == 0 else -1.0


def _weighted_features(tokens: Sequence[str]) -> Iterable[tuple[int, float]]:
    for position, token in enumerate(tokens):
        token_key = f"tok:{token}"
        base_weight = 1.0 + (len(token) % 7) * 0.05
        yield _hash_to_index(token_key), base_weight * _hash_to_sign(token_key)
        if position + 1 < len(tokens):
            bigram = f"{token} {tokens[position + 1]}"
            bigram_key = f"bigram:{bigram}"
            yield _hash_to_index(bigram_key), 0.5 * _hash_to_sign(bigram_key)


def embed_text(text: str) -> list[float]:
    """Return a deterministic local embedding vector for demo and tests only."""

    tokens = _normalize_text(text)
    vector = [0.0] * EMBEDDING_DIMENSION
    if not tokens:
        return vector

    for index, value in _weighted_features(tokens):
        vector[index] += value

    length = math.sqrt(sum(component * component for component in vector))
    if length == 0.0:
        return vector
    return [component / length for component in vector]


def embed_query(text: str) -> list[float]:
    return embed_text(text)
