import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from models import DocumentRecord, ProcessingResult
from storage import DocumentDatabase, FileStorage

from .extractor import DocumentTextExtractor
from .llm import LLMProvider


class DocumentPipeline:
    def __init__(
        self,
        extractor: DocumentTextExtractor,
        llm: LLMProvider,
        files: FileStorage,
        database: DocumentDatabase,
        max_llm_chars: int = 50_000,
    ) -> None:
        self.extractor = extractor
        self.llm = llm
        self.files = files
        self.database = database
        self.max_llm_chars = max_llm_chars

    def process(self, source: Path, original_filename: str, telegram_user_id: int) -> ProcessingResult:
        document_id = uuid4().hex
        destination = self.files.original_path(document_id, original_filename)
        if source.resolve() != destination.resolve():
            shutil.copy2(source, destination)

        extraction = self.extractor.extract(destination)
        warnings = list(extraction.warnings)
        if not extraction.text.strip():
            raise ValueError('No text recognized. Check image quality and OCR configuration. The original was saved.')
        llm_text = extraction.text[: self.max_llm_chars]
        if len(extraction.text) > self.max_llm_chars:
            warnings.append(f"Only the first {self.max_llm_chars} characters were sent to the LLM; the TXT contains all text.")
        metadata = self.llm.analyze_document(llm_text, original_filename, destination)
        text_path = self.files.save_text(document_id, extraction.text)
        metadata_path = self.files.save_metadata(document_id, metadata)
        record = DocumentRecord(
            id=document_id,
            telegram_user_id=telegram_user_id,
            original_filename=original_filename,
            original_path=str(destination),
            text_path=str(text_path),
            metadata_path=str(metadata_path),
            created_at=datetime.now(timezone.utc),
            metadata=metadata,
        )
        self.database.add(record, extraction.text)
        return ProcessingResult(document=record, warnings=warnings)

    def reanalyze(self, record: DocumentRecord) -> ProcessingResult:
        """Reuse stored OCR: never rerun OCR to change the semantic analysis."""
        text = Path(record.text_path).read_text(encoding='utf-8')
        metadata = self.llm.analyze_document(text[:self.max_llm_chars], record.original_filename, Path(record.original_path))
        history = self.files.data_dir / 'history' / record.id
        history.mkdir(parents=True, exist_ok=True)
        shutil.copy2(record.metadata_path, history / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f') + '.json'))
        updated = record.model_copy(update={'metadata': metadata})
        self.files.save_metadata(record.id, metadata)
        self.database.update_metadata(updated)
        return ProcessingResult(document=updated)
