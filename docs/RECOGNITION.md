# From messy OCR to useful document fields

[Home](../README.md)

These lessons come from the original LUX integration. References to result cards
and a reanalysis button describe a private interface deliberately excluded from
this repository. The public core exposes `DocumentPipeline.reanalyze(record)`.

## Configuration, not training

No weights were trained. There was no fine-tuning or self-learning from uploads.
Improvements came from a pretrained vision model, clearer instructions, a response
schema, conservative checks, and more useful presentation.

The early `LocalMetadataProvider` uses regex rules, the first OCR line as a title,
and initial text fragments as a summary. It does not understand party roles:
OCR noise, app buttons, and address blocks can all appear in its description.

| Change | Purpose |
|---|---|
| `LLM_PROVIDER=ollama`, Qwen3-VL 4B Instruct | Semantic extraction instead of regex rules |
| Image plus OCR for photos | Layout and visual context |
| Explicit party, money, and date instructions | Distinguish field meanings |
| JSON Schema + Pydantic | Enforce structure/types and reject extra fields |
| `quality.py` | Remove some unsupported or inappropriate values |
| Separate card fields | A short description instead of an OCR dump |

Pydantic validates structure, **not truth**. `temperature=0` reduces variation;
it does not guarantee accuracy or complete determinism.

## Typical mistakes, without private data

In a payment reminder, the current outstanding amount may differ from the original
invoice amount. The addressee is not necessarily the service provider, and the letter
date is not the payment deadline. The schema therefore separates `amount`,
`original_amount`, `sender`, `recipient`, `counterparty`, `date`,
`invoice_date`, and `due_date`.

A banking screenshot containing `SEPA Lastschrift-Rückgabe` describes a returned
direct debit, not a completed payment or a new invoice. Postprocessing clears invoice
dates/deadlines for bank transactions and labels recognizable returned-debit markers.
Damaged OCR can defeat the rule: it is a heuristic.

Do not invent blurry addresses. `address_supported` approximately matches meaningful
words in the first address segment against OCR with a 0.84 similarity threshold.
It does **not** verify the house number, postcode, or existence of an address.
Bad OCR can cause even a correct address to be removed. Do not lower the threshold
just to fill more fields.

One experiment increased sharpness/contrast and changed OCR mode on a poor photo.
It made that sample worse and was reverted. This does not prove all preprocessing
is useless; it means a universal enhancement step was not supported by the example.
The production path does not make repeated OCR passes over every file.

## Actual settings and limitations

- Image input receives EXIF orientation correction, a 1920×1920 size cap, and JPEG
  quality 92 before model inference. The separate OCR path does not apply that correction.
- Ollama code sets `temperature=0`, `num_ctx=8192`, `num_predict=1800`,
  and `keep_alive=5m`. These are not environment or UI settings.
- Pipeline text is capped by `MAX_LLM_CHARS` (50,000 by default), then Ollama
  applies an additional 18,000-character cap. Raising only MAX_LLM_CHARS is insufficient.
- JPG/PNG supply image input. PDFs supply extracted text, not rendered page images.
- Any nonempty PDF page text skips OCR, even when that text layer is poor.
- DOCX reads paragraphs and tables; embedded pictures, headers/footers, and complex layout are not guaranteed.
- Empty OCR stops processing before inference; there is no vision-only fallback.
- `quality.py` rewrites some titles/summaries. Changing the prompt alone may not change the final result.
- Detailed model review notes may be replaced by a generic warning; this is not calibrated confidence.
- This public example generates English summaries and labels. Proper names and
  addresses stay in their original language. The private installation originally used Russian.

Two observed runs on the original laptop took approximately 155 and 38 seconds.
These are individual observations, not a performance guarantee.

## Improve quality without fooling yourself

1. Preserve the original, TXT, and JSON baseline. Use synthetic/anonymized shared tests.
2. Write expected fields manually. Keep genuinely unknown values unknown.
3. Locate the failing layer: image → OCR → interpretation → postprocessing → presentation.
4. Change one factor: prompt, model, image parameter, or rule.
5. Compare different documents. Never hardcode a sample's name, amount, or address.
6. Count correct fields, invented values, omissions, and latency. Fluent prose does not prove accuracy.
7. Add a regression test and revert changes that make the relevant cases worse.
8. Update documentation. Obtain separate agreement before reprocessing a whole archive.

Example reference format (an automated benchmark for this format is not implemented):

```json
{
  "sample": "synthetic-reminder-01",
  "expected": {
    "document_type": "payment_reminder",
    "sender": "Example Services GmbH",
    "amount": "105.00",
    "original_amount": "100.00",
    "currency": "EUR",
    "recipient_address": null
  },
  "must_not": ["invent_address", "classify_as_completed_payment"]
}
```

Reanalysis is suitable for prompt/model/postprocessing changes and reuses saved TXT.
Test OCR changes separately on controlled copies, not through hidden extra passes
inside the normal queue.

## Better input photos

Capture the whole page, straight and evenly lit, without glare or shadows. Check
small digits at full size. Do not crop headers or field labels. Prefer the original
text PDF over a screenshot. Do not upload passwords for experiments.
A larger model may help, but still requires quality and resource checks.
