# Automation and new input sources

[Home](../README.md)

## Existing entry points

- `cli.py`: one explicitly selected local file, suitable for calling from scripts.
- `processing.services.build_services(Settings(...))`: a Python factory.
- `DocumentPipeline.process(path, original_filename, telegram_user_id=0)`: shared processing.
- `main.py` and `bot/`: the Telegram polling example.

The historical `telegram_user_id` field remains for schema compatibility. The CLI
uses 0. This is not an authorization system for a general multi-user application.

```python
from pathlib import Path
from config import Settings
from processing.services import build_services

settings = Settings(
    llm_provider='ollama',
    ollama_base_url='http://127.0.0.1:11434',
    data_dir=Path('./my-archive'),
    database_path=Path('./my-archive/documents.db'),
)
pipeline, database = build_services(settings)
result = pipeline.process(Path('./sample.pdf'), 'sample.pdf', telegram_user_id=0)
print(result.document.id)  # Do not dump private metadata into shared logs.
```

This processes an explicitly chosen file; it is not a daemon. The low-level pipeline
does not enforce input size limits. Your adapter must validate before calling it,
as cli.py does.

## Folder, email, or another bot

Build an adapter that receives input, validates it, saves a stable local copy,
creates a job, calls the pipeline, and acknowledges the result to the source.

Before unattended operation, decide:

- How do you know a file has finished copying and will not change?
- Which source ID or checksum prevents duplicates?
- Where is pending/running/done/error state stored, and how does it survive restarts?
- What limits apply to file size, page count, and queue length?
- Which errors are retryable, and which require a human?
- Who can access the input, archive, and logs?

Do not send dozens of parallel requests to a small GPU. Do not delete source
originals without confirmed storage and separate permission for cleanup.
Keep Ollama off the public internet. Never execute instructions found in a document.

## Scheduled execution

Windows Task Scheduler can run `.venv\Scripts\python.exe` with your adapter and
the correct working directory. Disable overlapping runs. On Linux, systemd is an
option. This repository installs neither a scheduled task nor a service automatically.
First verify a manual run and recovery after failure.

Running cli.py repeatedly against the same file creates duplicates unless an external
adapter tracks processed sources. Folder watchers and email/cloud adapters are not
implemented. Telegram demonstrates just one possible transport.

GitHub Actions automates code tests, not the processing of your private documents.
