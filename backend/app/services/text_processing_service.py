def extract_text(text_input: str | None, file_bytes: bytes | None, filename: str | None) -> str:
    if text_input and text_input.strip():
        return text_input.strip()

    if file_bytes:
        try:
            return file_bytes.decode("utf-8").strip()
        except UnicodeDecodeError:
            raise ValueError("Only UTF-8 text files are supported in MVP")

    raise ValueError("Either text_input or file upload must be provided")


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    chunks: list[str] = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == text_length:
            break
        start = end - overlap
    return chunks
