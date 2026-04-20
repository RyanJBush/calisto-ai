import re


class SecurityTextService:
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    PHONE_PATTERN = re.compile(r"\b(?:\+1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?){2}\d{4}\b")
    SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
    PROMPT_INJECTION_PATTERNS = [
        re.compile(r"ignore (all )?previous instructions", re.IGNORECASE),
        re.compile(r"system prompt", re.IGNORECASE),
        re.compile(r"reveal (your|the) instructions", re.IGNORECASE),
        re.compile(r"act as .*developer", re.IGNORECASE),
    ]

    def redact_pii(self, content: str) -> str:
        redacted = self.EMAIL_PATTERN.sub("[REDACTED_EMAIL]", content)
        redacted = self.PHONE_PATTERN.sub("[REDACTED_PHONE]", redacted)
        redacted = self.SSN_PATTERN.sub("[REDACTED_SSN]", redacted)
        return redacted

    def sanitize_prompt_injection(self, content: str) -> str:
        sanitized = content
        for pattern in self.PROMPT_INJECTION_PATTERNS:
            sanitized = pattern.sub("[FILTERED_INSTRUCTION]", sanitized)
        return sanitized
