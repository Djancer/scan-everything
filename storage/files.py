import json
import re
from pathlib import Path

from models import DocumentMetadata


class FileStorage:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.originals_dir = data_dir / "originals"
        self.text_dir = data_dir / "text"
        self.metadata_dir = data_dir / "metadata"
        for directory in (self.originals_dir, self.text_dir, self.metadata_dir):
            directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def safe_filename(filename: str) -> str:
        clean = re.sub(r"[^\w. -]", "_", Path(filename).name, flags=re.UNICODE).strip(" .")
        return clean[:180] or "document"

    def original_path(self, document_id: str, filename: str) -> Path:
        return self.originals_dir / f"{document_id}_{self.safe_filename(filename)}"

    def save_text(self, document_id: str, text: str) -> Path:
        path = self.text_dir / f"{document_id}.txt"
        path.write_text(text, encoding="utf-8")
        return path

    def save_metadata(self, document_id: str, metadata: DocumentMetadata) -> Path:
        path = self.metadata_dir / f"{document_id}.json"
        path.write_text(
            json.dumps(metadata.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

