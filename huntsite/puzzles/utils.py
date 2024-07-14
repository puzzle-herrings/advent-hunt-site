import unicodedata


def clean_answer(text: str) -> str:
    """Clean up an answer or guess by:

    - Uppercasing the text
    - Stripping leading/trailing whitespace
    - Replacing any internal whitespace with a single space
    - Dropping non-alphabetic characters
    """
    nfkd_form = unicodedata.normalize("NFKD", text.strip())
    cleaned = "".join(c.upper() for c in nfkd_form if c.isalpha() or c.isspace())
    cleaned = " ".join(cleaned.split())
    return cleaned


def normalize_answer(text: str) -> str:
    """Normalizes an answer to a consistent format for comparison. Does everything
    that clean_answer does and removes whitespace.
    """
    normalized = "".join(clean_answer(text).split())
    return normalized
