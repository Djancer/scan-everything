# How the original LUX integration worked

[Home](../README.md)

This describes the original private system, not a bundled web panel.

## Original architecture

1. A lightweight Telegram receiver on a server saved originals and a manifest with IDs/hashes.
2. A PC periodically downloaded new files over SSH/SFTP.
3. A shared queue processed OCR and Qwen sequentially, saving TXT/JSON/SQLite.
4. A private local web panel displayed fields and download links.
5. Metadata returned to the server; the bot sent a short result card.

When the PC was off, the server kept receiving files. Closing the browser did not
stop the backend. The heavy model ran on the PC, not on the memory-limited server.

## What this repository reuses

The public example contains the pipeline, providers, schemas, and checks.
`processing/services.py` is a transport-independent factory.
`cli.py` is a minimal local-file adapter. `main.py` is a standalone Telegram bot:
it downloads and processes files on the same machine. It is **not** the original
split relay and does not include a server queue for an offline PC.

Synchronization, the private UI, its queue.json/HTTP API, launcher, and visual design
are excluded. You can build a separate interface over the core, but none is required
to use this example. Never copy a private archive or credentials to set it up.

## Responsibility boundaries

Adapters own delivery, source IDs, limits, access control, and retries.
The pipeline owns extraction, interpretation, and storage. A UI owns presentation.
Replacing Telegram with a folder or email means adding an adapter, not rewriting OCR.

Reliable automation needs persistent job state and duplicate protection.
A timer repeatedly calling `process()` does not provide either.
