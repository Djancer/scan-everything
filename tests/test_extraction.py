import tempfile
import unittest
from pathlib import Path

import pymupdf
from PIL import Image

from processing.extractor import DocumentTextExtractor
from processing.ocr import DisabledOCRProvider, OCRProvider


class CountingOCR(OCRProvider):
    def __init__(self) -> None:
        self.calls = 0

    def extract_image(self, image: Image.Image) -> str:
        self.calls += 1
        return "OCR text"


class ExtractionTest(unittest.TestCase):
    def test_text_pdf_does_not_use_ocr(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "text.pdf"
            pdf = pymupdf.open()
            page = pdf.new_page()
            page.insert_text((72, 72), "A PDF text layer")
            pdf.save(path)
            pdf.close()

            ocr = CountingOCR()
            result = DocumentTextExtractor(ocr).extract(path)
            self.assertIn("A PDF text layer", result.text)
            self.assertEqual(ocr.calls, 0)
            self.assertFalse(result.used_ocr)

    def test_image_without_ocr_is_saved_with_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "scan.png"
            Image.new("RGB", (20, 20), "white").save(path)
            result = DocumentTextExtractor(DisabledOCRProvider()).extract(path)
            self.assertEqual(result.text, "")
            self.assertTrue(result.warnings)
            self.assertIn("disabled", result.warnings[0].lower())


if __name__ == "__main__":
    unittest.main()
