"""Conservative rules, not an AI model. No invented fields and no API costs."""
import re
from decimal import Decimal
from pathlib import Path
from datetime import date

from models import DocumentMetadata
from .base import LLMProvider


class LocalMetadataProvider(LLMProvider):
    def extract_metadata(self, text: str, filename: str) -> DocumentMetadata:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        folded = text.casefold()
        kind = 'other'
        for candidate, words in [('invoice', ['invoice', 'rechnung', 'счёт', 'счет']),
                                 ('contract', ['contract', 'vertrag', 'договор']),
                                 ('receipt', ['receipt', 'quittung', 'кассовый чек'])]:
            if any(word in folded for word in words):
                kind = candidate
                break
        amount, currency = None, None
        # Only explicit totals, not arbitrary numbers in the document.
        matches = re.findall(r'(?:total|gesamt(?:betrag)?|итого|к оплате|amount due)\s*:?\s*([\d .,]+)\s*(EUR|USD|RUB|€|\$|₽)', text, re.I)
        if matches:
            value, unit = matches[-1]
            value = value.replace(' ', '')
            if ',' in value and '.' in value:
                value = value.replace('.', '').replace(',', '.') if value.rfind(',') > value.rfind('.') else value.replace(',', '')
            else:
                value = value.replace(',', '.')
            try:
                amount = Decimal(value)
                currency = {'€': 'EUR', '$': 'USD', '₽': 'RUB'}.get(unit, unit.upper())
            except Exception:
                pass
        stamp = re.search(r'\b(20\d{2}-\d{2}-\d{2})\b', text)
        date_value = None
        if stamp:
            try:
                date_value = date.fromisoformat(stamp[1]).isoformat()
            except ValueError:
                pass
        return DocumentMetadata(document_type=kind, title=(lines[0] if lines else Path(filename).stem)[:160],
                                summary=' '.join(lines)[:400], date=date_value, amount=amount,
                                currency=currency, tags=[kind, 'local-rules'])
