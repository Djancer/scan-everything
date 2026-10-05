from abc import ABC, abstractmethod
from pathlib import Path

from models import DocumentMetadata


class LLMProvider(ABC):
    def analyze_document(self, text: str, filename: str, source: Path | None = None) -> DocumentMetadata:
        return self.extract_metadata(text, filename)

    @abstractmethod
    def extract_metadata(self, text: str, filename: str) -> DocumentMetadata:
        """Turn document text into the shared, validated metadata contract."""
