import tempfile
import unittest
from pathlib import Path

from docx import Document

from bot.application import build_services
from config import Settings


class PipelineSmokeTest(unittest.TestCase):
    def test_docx_pipeline_and_search(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "invoice.docx"
            docx = Document()
            docx.add_paragraph("Test Invoice\nTotal 42.00 EUR")
            docx.save(source)
            settings = Settings(
                llm_provider="mock",
                ocr_provider="disabled",
                data_dir=root / "data",
                database_path=root / "data" / "documents.db",
            )
            pipeline, database = build_services(settings)
            result = pipeline.process(source, source.name, 123)
            self.assertEqual(result.document.metadata.document_type, "invoice")
            self.assertTrue(Path(result.document.original_path).exists())
            self.assertTrue(Path(result.document.text_path).exists())
            self.assertTrue(Path(result.document.metadata_path).exists())
            self.assertEqual(len(database.recent(123)), 1)
            self.assertEqual(len(database.search(123, "invoice")), 1)


if __name__ == "__main__":
    unittest.main()

