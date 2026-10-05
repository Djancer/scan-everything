"""Transport-independent factory: no Telegram runtime or web UI required."""
from config import Settings
from storage import DocumentDatabase, FileStorage
from .extractor import DocumentTextExtractor
from .llm import create_llm_provider
from .ocr import DisabledOCRProvider, TesseractOCRProvider
from .pipeline import DocumentPipeline


def build_services(settings: Settings) -> tuple[DocumentPipeline, DocumentDatabase]:
    files = FileStorage(settings.data_dir)
    database = DocumentDatabase(settings.database_path)
    database.initialize()
    ocr = (DisabledOCRProvider() if settings.ocr_provider == 'disabled' else
           TesseractOCRProvider(settings.tesseract_lang, settings.tesseract_cmd))
    pipeline = DocumentPipeline(DocumentTextExtractor(ocr), create_llm_provider(settings),
                                files, database, settings.max_llm_chars)
    return pipeline, database
