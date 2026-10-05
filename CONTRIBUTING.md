# Contributing

Read [AGENTS.md](AGENTS.md) and [Automation](docs/AUTOMATION.md).
Keep the processing core separate from input adapters. For OCR/LLM changes,
save a baseline and add regression tests using synthetic data.
Do not add personal documents, runtimes, tokens, or the private LUX interface.

Run `python main.py --check` and `python -m unittest discover -s tests -v`.
Mocks do not establish model accuracy. Update guides when contracts change.

English is the primary language for code comments, messages, guides, and the agent
skill. Keep [README.ru.md](README.ru.md) aligned with the English introduction.
Preserve multilingual recognition keywords and original-language document evidence.

The owner has not chosen a license yet; terms for external contributions need agreement.
