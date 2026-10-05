import tempfile
import unittest
from pathlib import Path
from docx import Document
from config import Settings
from cli import process_file


class LocalAdapterTest(unittest.TestCase):
    def test_mock_local_file_without_telegram(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'sample.docx'
            doc = Document()
            doc.add_paragraph('Invoice Total: 12.00 EUR')
            doc.save(source)
            settings = Settings(_env_file=None, llm_provider='mock', ocr_provider='disabled')
            result = process_file(source, root / 'archive', settings)
            self.assertEqual(result.document.telegram_user_id, 0)
            self.assertTrue(Path(result.document.text_path).is_file())
            self.assertTrue((root / 'archive/documents.db').is_file())
            self.assertTrue(source.is_file())

    def test_reject_unsupported_without_creating_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'not-a-document.exe'
            source.write_bytes(b'not executable')
            with self.assertRaises(ValueError):
                process_file(source, root / 'archive', Settings(_env_file=None, llm_provider='mock'))
            self.assertFalse((root / 'archive').exists())
