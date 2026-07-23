"""Conservative English prompt spacing, punctuation, article, and duplicate cleanup."""

import re

_SPACE_BEFORE_PUNCTUATION = re.compile(r"\s+([,.;:!?])")
_MISSING_SPACE_AFTER = re.compile(r"([,.;:!?])(?=[A-Za-z0-9])")
_REPEATED_PUNCTUATION = re.compile(r"([,.;:!?])(?:\s*\1)+")
_EMPTY_SEGMENTS = re.compile(r"(?:^|(?<=[.!?]))\s*[,;:]+\s*(?=$|[.!?])")
_SENTENCE_START = re.compile(r"(^|[.!?]\s+)([a-z])")
_BASIC_A = re.compile(r"\ba\s+([aeiou][A-Za-z-]*)\b", re.IGNORECASE)
_BASIC_AN = re.compile(r"\ban\s+([b-df-hj-np-tv-z][A-Za-z-]*)\b", re.IGNORECASE)
_SENTENCE = re.compile(r"([^.!?]+)([.!?]+|$)")


def normalize_prompt(text: str, *, convert_plus: bool = True) -> str:
    """Apply conservative normalization without promising universal grammar."""
    normalized = text.replace("+", " and ") if convert_plus else text
    normalized = re.sub(r"\s+", " ", normalized).strip()
    normalized = _SPACE_BEFORE_PUNCTUATION.sub(r"\1", normalized)
    normalized = _REPEATED_PUNCTUATION.sub(r"\1", normalized)
    normalized = _EMPTY_SEGMENTS.sub("", normalized)
    normalized = _MISSING_SPACE_AFTER.sub(r"\1 ", normalized)
    normalized = _fix_basic_articles(normalized)
    normalized = _deduplicate_sentences(normalized)
    normalized = _SENTENCE_START.sub(
        lambda match: match.group(1) + match.group(2).upper(), normalized
    )
    normalized = re.sub(r"\s+", " ", normalized).strip(" ,;:")
    return normalized


def normalize_fragment(text: str, *, convert_plus: bool = True) -> str:
    """Normalize a library fragment while retaining intentional final punctuation."""
    return normalize_prompt(text, convert_plus=convert_plus)


def _fix_basic_articles(text: str) -> str:
    def to_an(match: re.Match[str]) -> str:
        article = "An" if match.group(0)[0].isupper() else "an"
        return f"{article} {match.group(1)}"

    def to_a(match: re.Match[str]) -> str:
        article = "A" if match.group(0)[0].isupper() else "a"
        return f"{article} {match.group(1)}"

    return _BASIC_AN.sub(to_a, _BASIC_A.sub(to_an, text))


def _deduplicate_sentences(text: str) -> str:
    seen: set[str] = set()
    parts: list[str] = []
    for match in _SENTENCE.finditer(text):
        body = match.group(1).strip(" ,;:")
        punctuation = match.group(2)
        if not body:
            continue
        key = re.sub(r"\s+", " ", body).casefold()
        if key in seen:
            continue
        seen.add(key)
        parts.append(body + punctuation[:1])
    return " ".join(parts)
