import asyncio
import os
import sys
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, Application
)

import config
from file_utils import TempFileManager
from handlers import (
    cmd_start, cmd_help, cmd_cancel, show_tools_menu,
    handle_callback, handle_text_input, handle_document_upload
)
from security import logger


async def handle_health_check(reader, writer):
    """Handles HTTP health check requests from Render.com port scanner."""
    try:
        _ = await reader.read(1024)
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 19\r\n"
            "Connection: close\r\n\r\n"
            "GitKey Bot is Live!"
        )
        writer.write(response.encode('utf-8'))
        await writer.drain()
    except Exception as e:
        logger.debug(f"Health check socket note: {e}")
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass


async def start_health_check_server(port: int):
    """Starts a lightweight asyncio HTTP server on 0.0.0.0:PORT to satisfy Render.com Web Service port binding."""
    try:
        server = await asyncio.start_server(handle_health_check, '0.0.0.0', port)
        logger.info(f"Health check HTTP server listening on 0.0.0.0:{port} (Satisfies Render.com port scan)")
        async with server:
            await server.serve_forever()
    except Exception as e:
        logger.error(f"Failed to start health check HTTP server on port {port}: {e}")


async def periodic_cleanup_task():
    """Background task to clean up expired temporary files periodically."""
    while True:
        try:
            TempFileManager.cleanup_expired_temp_files()
        except Exception as e:
            logger.error(f"Error in periodic cleanup task: {e}")
        await asyncio.sleep(600)  # Run every 10 minutes


async def post_init(application: Application):
    """Post-initialization hook called by python-telegram-bot after loop starts."""
    port = config.PORT
    logger.info(f"Initializing background health check server on port {port}...")
    asyncio.create_task(start_health_check_server(port))
    asyncio.create_task(periodic_cleanup_task())


def main():
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("CRITICAL ERROR: TELEGRAM_BOT_TOKEN environment variable is not set!")
        logger.error("Please configure TELEGRAM_BOT_TOKEN in your .env file or Render.com Environment Variables.")
        sys.exit(1)

    logger.info("Initializing GitKey Bot application...")

    app = (
        ApplicationBuilder()
        .token(config.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

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
        logger.info("Starting polling mode (with background health check HTTP server for Render.com)...")
        app.run_polling()


if __name__ == "__main__":
    main()
