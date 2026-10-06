import asyncio
import sys
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
)

import config
from file_utils import TempFileManager
from handlers import (
    cmd_start, cmd_help, cmd_cancel, show_tools_menu,
    handle_callback, handle_text_input, handle_document_upload
)
from security import logger


async def periodic_cleanup_task():
    """Background task to clean up expired temporary files periodically."""
    while True:
        try:
            TempFileManager.cleanup_expired_temp_files()
        except Exception as e:
            logger.error(f"Error in periodic cleanup task: {e}")
        await asyncio.sleep(600)  # Run every 10 minutes


def main():
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("CRITICAL ERROR: TELEGRAM_BOT_TOKEN environment variable is not set!")
        logger.error("Please configure TELEGRAM_BOT_TOKEN in your .env file or Render.com Environment Variables.")
        sys.exit(1)

    logger.info("Initializing GitKey Bot application...")

    app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Command Handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("tools", show_tools_menu))
    app.add_handler(CommandHandler("cancel", cmd_cancel))

    # Callback Query Handler
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Message Handlers
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_input))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document_upload))

    logger.info("GitKey Bot is starting...")

    # Choose Polling or Webhook based on configuration
    if config.USE_WEBHOOK and config.WEBHOOK_URL:
        logger.info(f"Starting webhook on port {config.PORT} with URL {config.WEBHOOK_URL}...")
        app.run_webhook(
            listen="0.0.0.0",
            port=config.PORT,
            url_path=config.TELEGRAM_BOT_TOKEN,
            webhook_url=f"{config.WEBHOOK_URL}/{config.TELEGRAM_BOT_TOKEN}"
        )
    else:
        logger.info("Starting polling mode...")
        app.run_polling()


if __name__ == "__main__":
    main()
