# Troubleshooting

[Home](../README.md)

| Symptom | Check |
|---|---|
| Messy summaries again | `local` uses regex rules; select `ollama`. Compare original, TXT, and JSON. |
| Connection refused | Is Ollama running? Do ports 11434/11435 match your configuration? |
| Model not found | Do `ollama list/pull` target the same server instance? |
| OCR unavailable | Check the executable, `--list-langs`, and TESSERACT_LANG. |
| Empty OCR | Check image clarity, orientation, and languages. There is no vision-only fallback. |
| PDF worse than JPG | PDFs are not sent as page images; a bad nonempty text layer skips OCR. |
| Address is null | It was not supported. Check the original instead of guessing. |
| Slow or timeout | Cold model, CPU/offload, memory: inspect `ollama ps` and process one file at a time. |
| Bot does not respond | Check the process, token, allowlist, and competing poller/webhook. |
| Duplicate records | CLI creates a new ID each time; adapters need deduplication. |
| Looking for the HTML panel | Deliberately excluded: this is a headless example. |

`main.py --check` does not test real inference. `--mock` does not improve recognition;
it tests storage and contracts. CLI provider failures intentionally omit raw exception
details to avoid leaking URLs, keys, or document text. Inspect exceptions locally
when debugging and redact diagnostics before sharing.

Bug reports should include Python/Ollama versions, provider mode, and a synthetic
reproduction, not your archive, `.env`, or real invoices. Calibrated confidence scores
are not implemented. JSON Schema is not a measure of factual accuracy.
