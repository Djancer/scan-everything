# Setup and Qwen

[Home](../README.md) · Documentation language: English

## 1. Source and Python

Choose **Code → Download ZIP** on GitHub and extract to a new folder, for example
`C:\Projects\scan-everything`, not into an existing personal LUX archive.
Install [Python 3.12](https://www.python.org/downloads/windows/).

```powershell
cd C:\Projects\scan-everything
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe main.py --check
```

Copy the environment template only on first setup; do not overwrite existing settings.
Virtual-environment activation is optional. On Linux, use `python3 -m venv .venv`
and `.venv/bin/python`; Windows is the main tested path for this example.

## 2. OCR

Follow the [Tesseract installation guide](https://tesseract-ocr.github.io/tessdoc/Installation.html)
for your OS. Check the source of any Windows build. Install the languages your
documents need (such as eng/deu/rus), then verify:

```powershell
& 'C:\Program Files\Tesseract-OCR\tesseract.exe' --list-langs
```

Configure `.env`:

```dotenv
OCR_PROVIDER=tesseract
TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe
TESSERACT_LANG=eng+deu
```

OCR language and summary language are different: OCR must match the source document.
The public example writes English summaries while preserving original names and addresses.
Text-based PDF/DOCX can be tested without OCR. Images with empty extracted text
do not reach the model, even if a vision model could theoretically read them.

## 3. The model and its runtime are separate

Install and start [Ollama for Windows](https://docs.ollama.com/windows).
Qwen is the model; Ollama is the process serving its local API. The standard port is 11434.

```powershell
ollama pull qwen3-vl:4b-instruct
ollama list
Invoke-RestMethod http://127.0.0.1:11434/api/version
```

The [vision model](https://ollama.com/library/qwen3-vl:4b-instruct) download was about
3.3 GB in the original setup. Check the current model page before downloading.
You also need RAM/VRAM and storage for the runtime and documents. One working setup
used 32 GB RAM and an RTX 3050 Laptop with 4 GB VRAM; that is an observation, not a
minimum requirement. CPU-only inference can be much slower. Test your own hardware.

```dotenv
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3-vl:4b-instruct
OLLAMA_TIMEOUT=600
```

No API key is required. `local` means regex rules, `mock` means fake test metadata,
and `ollama` means local AI. Do not select a cloud model tag for a local-only workflow.

## 4. First real document

```powershell
.\.venv\Scripts\python.exe cli.py 'C:\Samples\invoice.pdf' --output-dir '.\data'
```

Begin with a synthetic document. Compare saved TXT/JSON against the original, then
try a clear JPG. OCR errors and interpretation errors are different problems.
Do not paste secrets into terminals or public issues.

Outputs are stored under originals/, text/, metadata/, and documents.db within
output-dir. Resubmission creates another record. To test without real inference:

```powershell
.\.venv\Scripts\python.exe cli.py 'C:\Samples\invoice.pdf' --mock --output-dir '.\test-data'
```

## Optional isolated Ollama

The official installation guide offers a standalone ZIP. Launch a separate instance
in one PowerShell window with your chosen model directory:

```powershell
$env:OLLAMA_HOST='127.0.0.1:11435'
$env:OLLAMA_MODELS='C:\Models\scan-everything'
$env:OLLAMA_NO_CLOUD='1'
ollama serve
```

In another window, set the same `OLLAMA_HOST` before running `ollama pull`.
Set `OLLAMA_BASE_URL=http://127.0.0.1:11435` in the project's `.env`.
The CLI does not start Ollama. Editing `.env` does not reconfigure an already
running model server. Do not start two servers on the same port.

This package does not bundle model weights, a Python runtime, or a one-click installer.
