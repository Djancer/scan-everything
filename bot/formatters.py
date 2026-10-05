from html import escape

from models import DocumentRecord, ProcessingResult


def result_card(result: ProcessingResult) -> str:
    metadata = result.document.metadata
    amount = "—"
    if metadata.amount is not None:
        amount = f"{metadata.amount} {metadata.currency or ''}".strip()
    tags = ", ".join(f"#{tag.replace(' ', '_')}" for tag in metadata.tags) or "—"
    warning = ""
    if result.warnings:
        warning = "\n\n⚠️ " + escape(" ".join(result.warnings))
    return (
        "✅ <b>Document processed</b>\n"
        f"<b>Type:</b> {escape(metadata.document_type)}\n"
        f"<b>Title:</b> {escape(metadata.title)}\n"
        f"<b>Summary:</b> {escape(metadata.summary)}\n"
        f"<b>Date:</b> {escape(metadata.date or '—')}\n"
        f"<b>Sender:</b> {escape(metadata.sender or '—')}\n"
        f"<b>Recipient:</b> {escape(metadata.recipient or '—')}\n"
        f"<b>Amount:</b> {escape(amount)}\n"
        f"<b>Due:</b> {escape(metadata.due_date or '—')}\n"
        f"<b>Tags:</b> {escape(tags)}\n"
        f"<b>ID:</b> <code>{escape(result.document.id)}</code>{warning}"
    )


def record_line(record: DocumentRecord) -> str:
    return (
        f"• <b>{escape(record.metadata.title)}</b> "
        f"({escape(record.metadata.document_type)})\n"
        f"  <code>{escape(record.id)}</code> · {record.created_at:%Y-%m-%d}"
    )

