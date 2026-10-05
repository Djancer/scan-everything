"""Explicit local-file adapter. No UI, background watcher or Telegram connection."""
import argparse
from pathlib import Path

from config import Settings
from processing.extractor import SUPPORTED_EXTENSIONS
from processing.services import build_services


def process_file(source: Path, output: Path, settings: Settings):
    source = source.resolve(strict=True)
    if not source.is_file() or source.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError('Expected a PDF, DOCX, JPG/JPEG or PNG file.')
    if source.stat().st_size > settings.max_file_mb * 1024 * 1024:
        raise ValueError('File exceeds MAX_FILE_MB.')
    output = output.resolve()
    settings = settings.model_copy(update={'data_dir': output, 'database_path': output / 'documents.db'})
    pipeline, _ = build_services(settings)
    return pipeline.process(source, source.name, telegram_user_id=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', type=Path)
    parser.add_argument('--output-dir', type=Path, default=Path('./data'))
    parser.add_argument('--mock', action='store_true', help='Test metadata; not real AI recognition')
    parser.add_argument('--allow-remote', action='store_true', help='Explicitly permit configured API provider to receive text')
    args = parser.parse_args()
    settings = Settings(llm_provider='mock') if args.mock else Settings()
    if settings.llm_provider == 'openai' and not args.allow_remote:
        parser.error('API provider sends text off-device. Use local Ollama or explicitly pass --allow-remote.')
    try:
        result = process_file(args.file, args.output_dir, settings)
    except Exception as exc:
        # Do not print provider exceptions containing URLs, source text or credentials.
        parser.exit(1, f'Processing failed ({type(exc).__name__}). Check input, OCR and provider settings.\n')
    print(f'Document saved: {result.document.id}')
    print('Original, TXT, JSON and SQLite are in the selected output directory.')
    for warning in result.warnings:
        print('Warning:', warning)


if __name__ == '__main__':
    main()
