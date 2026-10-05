import asyncio
import logging
import tempfile
from pathlib import Path

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from processing.extractor import SUPPORTED_EXTENSIONS, UnsupportedDocumentError
from processing.pipeline import DocumentPipeline
from storage import DocumentDatabase

from .formatters import record_line, result_card

logger = logging.getLogger(__name__)


class BotHandlers:
    def __init__(
        self,
        pipeline: DocumentPipeline,
        database: DocumentDatabase,
        allowed_user_ids: set[int] | None = None,
        max_file_bytes: int = 20 * 1024 * 1024,
    ) -> None:
        self.pipeline = pipeline
        self.database = database
        self.allowed_user_ids = allowed_user_ids or set()
        self.max_file_bytes = max_file_bytes

    async def _authorized(self, update: Update) -> bool:
        user = update.effective_user
        if user and (not self.allowed_user_ids or user.id in self.allowed_user_ids):
            return True
        if update.effective_message:
            await update.effective_message.reply_text("This bot is private.")
        return False

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self._authorized(update):
            return
        if update.effective_message:
            await update.effective_message.reply_text(
                "Send me a PDF, DOCX, JPG or PNG. I will save it locally, extract text, "
                "create structured metadata and index it.\n\n"
                "Commands:\n/recent — last documents\n/search <query> — search your archive"
            )

    async def recent(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self._authorized(update):
            return
        if not update.effective_user or not update.effective_message:
            return
        records = await asyncio.to_thread(self.database.recent, update.effective_user.id, 10)
        text = "<b>Recent documents</b>\n\n" + "\n\n".join(map(record_line, records)) if records else "No documents yet."
        await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

    async def search(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self._authorized(update):
            return
        if not update.effective_user or not update.effective_message:
            return
        query = " ".join(context.args).strip()
        if not query:
            await update.effective_message.reply_text("Usage: /search <query>")
            return
        records = await asyncio.to_thread(self.database.search, update.effective_user.id, query, 10)
        text = f"<b>Search results</b>\n\n" + "\n\n".join(map(record_line, records)) if records else "Nothing found."
        await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

    async def document(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self._authorized(update):
            return
        message = update.effective_message
        user = update.effective_user
        if not message or not user:
            return
        attachment = message.document or (message.photo[-1] if message.photo else None)
        if attachment is None:
            await message.reply_text("Please send a PDF, DOCX, JPG or PNG file.")
            return
        if attachment.file_size and attachment.file_size > self.max_file_bytes:
            await message.reply_text(
                f"File is too large. Maximum size: {self.max_file_bytes // (1024 * 1024)} MB."
            )
            return
        filename = getattr(message.document, "file_name", None) or f"telegram_photo_{attachment.file_unique_id}.jpg"
        suffix = Path(filename).suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            await message.reply_text("Unsupported file type. Use PDF, DOCX, JPG or PNG.")
            return

        status = await message.reply_text("⏳ Saving and processing the document…")
        try:
            telegram_file = await context.bot.get_file(attachment.file_id)
            with tempfile.TemporaryDirectory(prefix="document_bot_") as temp_dir:
                source = Path(temp_dir) / filename
                await telegram_file.download_to_drive(custom_path=source)
                result = await asyncio.to_thread(self.pipeline.process, source, filename, user.id)
            await status.edit_text(result_card(result), parse_mode=ParseMode.HTML)
        except UnsupportedDocumentError as exc:
            await status.edit_text(str(exc))
        except Exception:
            logger.exception("Document processing failed")
            await status.edit_text("❌ Processing failed. Check the local log for details.")
