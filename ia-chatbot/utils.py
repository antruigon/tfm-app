import re


def clean_mention(text: str) -> str:
    return re.sub(r"<@[^>]+>", "", text).strip()
