from io import BytesIO


class FileParserService:
    TEXT_MIME_TYPES = {"text/plain", "text/markdown", "application/json"}

    def extract_text(self, *, filename: str, content_type: str | None, payload: bytes) -> str:
        normalized_type = (content_type or "").lower()
        if normalized_type in self.TEXT_MIME_TYPES or filename.lower().endswith((".txt", ".md", ".json")):
            return payload.decode("utf-8", errors="ignore").strip()

        if normalized_type == "application/pdf" or filename.lower().endswith(".pdf"):
            return self._extract_pdf_text(payload)

        raise ValueError("Unsupported file type. Upload TXT, MD, JSON, or PDF documents.")

    def _extract_pdf_text(self, payload: bytes) -> str:
        try:
            from pypdf import PdfReader
        except Exception as exc:  # pragma: no cover - optional dependency
            raise ValueError("PDF parsing requires optional dependency 'pypdf'.") from exc

        reader = PdfReader(BytesIO(payload))
        text = "\n".join((page.extract_text() or "").strip() for page in reader.pages).strip()
        if not text:
            raise ValueError("Unable to extract text from the uploaded PDF.")
        return text


file_parser_service = FileParserService()
