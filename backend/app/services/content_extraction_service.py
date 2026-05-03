import base64
import io


class ContentExtractionService:
    SUPPORTED_TYPES = {"txt", "md", "pdf"}

    def parse(self, *, content: str | None, file_data_base64: str | None, file_type: str | None) -> str:
        normalized_type = (file_type or "txt").lower().strip()
        if normalized_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"Unsupported file_type '{file_type}'. Use one of: txt, md, pdf.")

        if content and content.strip():
            return content.strip()
        if not file_data_base64:
            raise ValueError("Either content or file_data_base64 must be provided.")

        raw_bytes = base64.b64decode(file_data_base64, validate=True)
        if normalized_type in {"txt", "md"}:
            return raw_bytes.decode("utf-8", errors="ignore").strip()
        return self._extract_pdf_text(raw_bytes)

    def _extract_pdf_text(self, payload: bytes) -> str:
        try:
            from pypdf import PdfReader
        except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
            raise ValueError("PDF ingestion requires optional dependency 'pypdf'.") from exc
        reader = PdfReader(io.BytesIO(payload))
        text_parts = [page.extract_text() or "" for page in reader.pages]
        content = "\n\n".join(part.strip() for part in text_parts if part.strip()).strip()
        if not content:
            raise ValueError("Unable to extract text from PDF.")
        return content
