from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import Settings
from processing.services import build_services

from .handlers import BotHandlers


def build_application(settings: Settings) -> Application:
    settings.validate_runtime()
    pipeline, database = build_services(settings)
    handlers = BotHandlers(
        pipeline,
        database,
        allowed_user_ids=settings.allowed_user_ids,
        max_file_bytes=settings.max_file_mb * 1024 * 1024,
    )
    application = Application.builder().token(settings.telegram_bot_token).build()
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("recent", handlers.recent))
    application.add_handler(CommandHandler("search", handlers.search))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handlers.document))
    return application
