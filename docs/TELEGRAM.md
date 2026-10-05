# Telegram as an example adapter

[Home](../README.md)

This public example runs the complete bot **on the machine with OCR and the model**.
For the historical lightweight-server/PC split, see [Integration](INTEGRATION.md).
A ready-made relay is not included.

1. Verify the local CLI using [Setup](SETUP.md).
2. Create your own bot with the official [BotFather](https://t.me/BotFather) using `/newbot`.
3. Configure `.env` locally:

```dotenv
TELEGRAM_BOT_TOKEN=YOUR_OWN_TOKEN
TELEGRAM_ALLOWED_USER_IDS=YOUR_NUMERIC_TELEGRAM_USER_ID
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3-vl:4b-instruct
```

A numeric user ID is not a username or phone number. Obtain your own ID through a
trusted method; never publish your token to find it. Separate multiple IDs with commas.
**An empty allowlist permits everyone**: configure it before starting.

4. Make sure Ollama is running, then launch from the repository root:

```powershell
.\.venv\Scripts\python.exe main.py
```

5. In your bot, send `/start`, a synthetic document, `/recent`, and `/search invoice`.

Do not run two polling processes with the same token. An existing webhook also
needs inspection before switching transports.

When the bot process is off, it cannot receive or process documents itself.
Do not treat this as a guaranteed durable queue or a substitute for a relay.
With Ollama, text does not go to a cloud LLM, but uploaded files still pass through
Telegram. If a token leaks, revoke/reissue it through BotFather; deleting it from
a later Git commit is insufficient.

`bot/handlers.py` demonstrates sender checks, file download, pipeline calls, and
result cards. Another messenger needs a different adapter, not a different OCR engine.
