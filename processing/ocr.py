from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path

from PIL import Image


class OCRUnavailableError(RuntimeError):
    pass


class OCRProvider(ABC):
    @abstractmethod
    def extract_image(self, image: Image.Image) -> str:
        """OCR one already-decoded image exactly once."""

    def extract_path(self, path: Path) -> str:
        with Image.open(path) as image:
            return self.extract_image(image)

    def extract_bytes(self, data: bytes) -> str:
        with Image.open(BytesIO(data)) as image:
            return self.extract_image(image)


class TesseractOCRProvider(OCRProvider):
    def __init__(self, language: str = "eng", executable: str | None = None) -> None:
        self.language = language
        self.executable = executable

    def extract_image(self, image: Image.Image) -> str:
        try:
            import pytesseract

            if self.executable:
                pytesseract.pytesseract.tesseract_cmd = self.executable
            return pytesseract.image_to_string(image.convert("RGB"), lang=self.language, timeout=90).strip()
        except Exception as exc:
            if exc.__class__.__name__ in {"TesseractNotFoundError", "TesseractError"} or isinstance(exc, OSError):
                raise OCRUnavailableError(
                    "OCR is unavailable. Install Tesseract OCR, add it to PATH or set "
                    "TESSERACT_CMD. The original file is still saved."
                ) from exc
            raise


class DisabledOCRProvider(OCRProvider):
    def extract_image(self, image: Image.Image) -> str:
        raise OCRUnavailableError(
            "OCR is disabled (OCR_PROVIDER=disabled). The original file is still saved."
        )
