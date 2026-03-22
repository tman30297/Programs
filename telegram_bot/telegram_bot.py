#!/usr/bin/env python3
"""
Telegram Bot Template
A simple, extensible Telegram bot using python-telegram-bot

Usage:
    export TELEGRAM_BOT_TOKEN="your-token-here"
    python telegram_bot.py
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# --- Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "👋 Hello! I'm your Telegram bot.\n\n"
        "Available commands:\n"
        "/start - Show this message\n"
        "/help - Show help\n"
        "/echo <text> - Echo back your message\n"
        "/info - Bot information"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(
        "📚 *Help*\n\n"
        "Commands:\n"
        "/start - Welcome message\n"
        "/help - Show this message\n"
        "/echo <text> - Echo your message\n"
        "/info - Bot info\n"
        "\n_Just send me a message and I'll echo it back!_",
        parse_mode="Markdown"
    )


async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /echo command"""
    if not context.args:
        await update.message.reply_text("Usage: /echo <text>")
        return
    
    text = " ".join(context.args)
    await update.message.reply_text(text)


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /info command"""
    bot = context.bot
    me = await bot.get_me()
    
    await update.message.reply_text(
        f"🤖 *Bot Information*\n\n"
        f"Name: {me.full_name}\n"
        f"Username: @{me.username}\n"
        f"ID: {me.id}\n"
        f"Supports inline queries: {'Yes' if me.supports_inline_queries else 'No'}",
        parse_mode="Markdown"
    )


async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages (echo back)"""
    # Echo the message back
    await update.message.reply_text(
        f"📝 You said: {update.message.text}"
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")


# --- Main Entry Point ---

def main():
    if not BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN environment variable not set!")
        print("Run: export TELEGRAM_BOT_TOKEN='your-token-here'")
        print("\nTo get a bot token:")
        print("1. Open @BotFather on Telegram")
        print("2. Send /newbot command")
        print("3. Follow the instructions")
        return
    
    logger.info("Starting Telegram bot...")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("echo", echo_command))
    application.add_handler(CommandHandler("info", info_command))
    
    # Add message handler (echo)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start polling
    logger.info("Bot is running! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
