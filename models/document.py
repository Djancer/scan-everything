from datetime import datetime
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DocumentMetadata(BaseModel):
    """The strict contract returned by every LLM provider."""

    model_config = ConfigDict(extra="forbid")

    document_type: str = Field(description="Short type such as invoice, contract, letter, receipt, other")
    title: str
    summary: str
    date: str | None = Field(default=None, description="Document date in YYYY-MM-DD when known")
    sender: str | None = None
    recipient: str | None = None
    amount: Decimal | None = None
    currency: str | None = Field(default=None, description="ISO 4217 code such as EUR")
    due_date: str | None = Field(default=None, description="Due date in YYYY-MM-DD when known")
    tags: list[str] = Field(default_factory=list)
    sender_address: str | None = None
    recipient_address: str | None = None
    counterparty: str | None = Field(default=None, description='Company involved in a bank transaction; not necessarily sender or recipient')
    document_number: str | None = None
    invoice_date: str | None = None
    original_amount: Decimal | None = Field(default=None, description='Original invoice amount if different from amount currently requested')
    transaction_type: str | None = None
    review_notes: list[str] = Field(default_factory=list)
    analysis_method: str = 'rules'

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        return value.upper().strip() if value else None

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, values: list[str]) -> list[str]:
        return list(dict.fromkeys(v.strip().lower() for v in values if v.strip()))[:20]


class DocumentRecord(BaseModel):
    id: str
    telegram_user_id: int
    original_filename: str
    original_path: str
    text_path: str
    metadata_path: str
    created_at: datetime
    metadata: DocumentMetadata


class ProcessingResult(BaseModel):
    document: DocumentRecord
    warnings: list[str] = Field(default_factory=list)

    @property
    def original_path(self) -> Path:
        return Path(self.document.original_path)
