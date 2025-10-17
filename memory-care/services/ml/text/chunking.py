def split(text: str) -> list[str]:
    return [t.strip() for t in text.split('. ') if len(t.strip())>20]
