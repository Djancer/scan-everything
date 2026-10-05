import json
import sqlite3
from contextlib import closing
from pathlib import Path

from models import DocumentMetadata, DocumentRecord


class DocumentDatabase:
    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._fts_enabled = True

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with closing(self.connect()) as db, db:
            db.execute(
                """CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    telegram_user_id INTEGER NOT NULL,
                    original_filename TEXT NOT NULL,
                    original_path TEXT NOT NULL,
                    text_path TEXT NOT NULL,
                    metadata_path TEXT NOT NULL,
                    full_text TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    document_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )"""
            )
            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_documents_user_created "
                "ON documents(telegram_user_id, created_at DESC)"
            )
            try:
                db.execute(
                    "CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5("
                    "document_id UNINDEXED, title, summary, tags, full_text)"
                )
            except sqlite3.OperationalError:
                self._fts_enabled = False

    def add(self, record: DocumentRecord, full_text: str) -> None:
        metadata_json = record.metadata.model_dump_json()
        tags = " ".join(record.metadata.tags)
        with closing(self.connect()) as db, db:
            db.execute(
                """INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record.id,
                    record.telegram_user_id,
                    record.original_filename,
                    record.original_path,
                    record.text_path,
                    record.metadata_path,
                    full_text,
                    metadata_json,
                    record.metadata.document_type,
                    record.metadata.title,
                    record.metadata.summary,
                    tags,
                    record.created_at.isoformat(),
                ),
            )
            if self._fts_enabled:
                db.execute(
                    "INSERT INTO documents_fts(document_id, title, summary, tags, full_text) VALUES (?, ?, ?, ?, ?)",
                    (record.id, record.metadata.title, record.metadata.summary, tags, full_text),
                )

    def recent(self, user_id: int, limit: int = 10) -> list[DocumentRecord]:
        with closing(self.connect()) as db, db:
            rows = db.execute(
                "SELECT * FROM documents WHERE telegram_user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        return [self._row_to_record(row) for row in rows]

    def update_metadata(self, record: DocumentRecord) -> None:
        with closing(self.connect()) as db, db:
            db.execute('UPDATE documents SET metadata_json=?,document_type=?,title=?,summary=?,tags=? WHERE id=?',
                       (record.metadata.model_dump_json(), record.metadata.document_type, record.metadata.title,
                        record.metadata.summary, ' '.join(record.metadata.tags), record.id))
            if self._fts_enabled:
                db.execute('UPDATE documents_fts SET title=?,summary=?,tags=? WHERE document_id=?',
                           (record.metadata.title, record.metadata.summary, ' '.join(record.metadata.tags), record.id))

    def search(self, user_id: int, query: str, limit: int = 10) -> list[DocumentRecord]:
        terms = [term for term in query.replace('"', " ").split() if term]
        if not terms:
            return []
        with closing(self.connect()) as db, db:
            if self._fts_enabled:
                match_query = " AND ".join(f'"{term}"' for term in terms)
                rows = db.execute(
                    """SELECT d.* FROM documents d
                    JOIN documents_fts ON documents_fts.document_id = d.id
                    WHERE d.telegram_user_id = ? AND documents_fts MATCH ?
                    ORDER BY d.created_at DESC LIMIT ?""",
                    (user_id, match_query, limit),
                ).fetchall()
            else:
                pattern = f"%{query}%"
                rows = db.execute(
                    """SELECT * FROM documents WHERE telegram_user_id = ?
                    AND (title LIKE ? OR summary LIKE ? OR tags LIKE ? OR full_text LIKE ?)
                    ORDER BY created_at DESC LIMIT ?""",
                    (user_id, pattern, pattern, pattern, pattern, limit),
                ).fetchall()
        return [self._row_to_record(row) for row in rows]

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> DocumentRecord:
        metadata = DocumentMetadata.model_validate(json.loads(row["metadata_json"]))
        return DocumentRecord(
            id=row["id"],
            telegram_user_id=row["telegram_user_id"],
            original_filename=row["original_filename"],
            original_path=row["original_path"],
            text_path=row["text_path"],
            metadata_path=row["metadata_path"],
            created_at=row["created_at"],
            metadata=metadata,
        )
