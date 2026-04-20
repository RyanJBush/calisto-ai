import re

TOKEN_PATTERN = re.compile(r"[a-z0-9]{2,}")


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())
