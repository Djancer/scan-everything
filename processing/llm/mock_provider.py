import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

from models import DocumentMetadata

from .base import LLMProvider


class MockLLMProvider(LLMProvider):
    """Deterministic offline fallback; useful for setup checks, not real classification."""

    def extract_metadata(self, text: str, filename: str) -> DocumentMetadata:
        lowered = f"{filename}\n{text[:3000]}".lower()
        document_type = "invoice" if any(word in lowered for word in ("invoice", "rechnung", "betrag")) else "other"
        compact = " ".join(text.split())
        title = next((line.strip() for line in text.splitlines() if line.strip()), Path(filename).stem)
        amount = None
        match = re.search(r"(?<!\d)(\d{1,6}(?:[.,]\d{2}))\s*(€|eur|usd|\$)", lowered, re.I)
        if match:
            try:
                amount = Decimal(match.group(1).replace(",", "."))
            except InvalidOperation:
                pass
        currency = None
        if match:
            currency = "EUR" if match.group(2).lower() in {"€", "eur"} else "USD"
        return DocumentMetadata(
            document_type=document_type,
            title=title[:160],
            summary=(compact[:300] or "No text could be extracted; metadata created in mock mode."),
            amount=amount,
            currency=currency,
            tags=[document_type, "mock"],
        )

