import re


def clean_question(text: str) -> str:
    """Normalize malformed question stems without changing the answer choices."""
    text = str(text or "").strip()

    # Remove accidental contextual text appended after a stem-ending colon.
    text = re.sub(
        r"\s*:\s*(?=(?:when|in|while|for|under|during|after|before)\b).*?$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove a known accidental context suffix that sometimes appears without a colon.
    text = re.sub(r"\s+in a multi-site organization\.?$", "", text, flags=re.IGNORECASE)

    # A common malformed construction such as "The center is a:" becomes a natural stem.
    text = re.sub(
        r"\bis\s+(?:a|an|the)\s*:$",
        "is best described as",
        text,
        flags=re.IGNORECASE,
    )

    # Remove the remaining answer-introduction colon.
    text = re.sub(r"\s*:\s*$", "", text)
    text = re.sub(r"\s{2,}", " ", text).strip()

    # Keep the question visually complete when the source ended with a colon.
    if text and not text.endswith(("?", ".", "!")):
        text += "?"
    return text
