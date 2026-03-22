#!/usr/bin/env python3
"""
Discord Bot Template
A simple, extensible Discord bot using discord.py

Usage:
    export DISCORD_BOT_TOKEN="your-token-here"
    python discord_bot.py
"""

import os
import asyncio
import logging
from discord import Intents, Client, Message, Embed, Color

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PREFIX = "!"

# Set up Discord intents (what events the bot can see)
intents = Intents.default()
intents.message_content = True  # Required for reading messages

client = Client(intents=intents)


# --- Event Handlers ---

@client.event
async def on_ready():
    """Called when the bot is ready and connected"""
    logger.info(f"Logged in as {client.user} (ID: {client.user.id})")
    logger.info(f"Connected to {len(client.guilds)} guild(s)")

    # Set bot presence
    await client.change_presence(
        activity=type("Activity", (), {"type": 1, "name": "type !help"})()  # Watching
    )


@client.event
async def on_message(message: Message):
    """Called when a message is sent in any channel the bot can see"""
    # Ignore messages from bots (including self)
    if message.author.bot:
        return

    # Get message content (handle partial content for older intents)
    content = message.content
    if not content:
        return

    # Simple command router
    if content.startswith(PREFIX):
        await handle_command(message, content[len(PREFIX):].strip())


# --- Command Handler ---

async def handle_command(message: Message, command: str):
    """Route commands to their handlers"""
    parts = command.split()
    if not parts:
        return

    cmd = parts[0].lower()
    args = parts[1:]

    # Command routing
    commands = {
        "ping": cmd_ping,
        "help": cmd_help,
        "embed": cmd_embed,
        "echo": cmd_echo,
        "info": cmd_info,
    }

    handler = commands.get(cmd)
    if handler:
        try:
            await handler(message, args)
        except Exception as e:
            logger.error(f"Error in command {cmd}: {e}")
            await message.reply(f"❌ Error: {e}")


# --- Commands ---

async def cmd_ping(message: Message, args: list):
    """Check bot latency"""
    latency = round(client.latency * 1000)
    await message.reply(f"🏓 Pong! Latency: {latency}ms")


async def cmd_help(message: Message, args: list):
    """Show help message"""
    embed = Embed(
        title="📚 Bot Commands",
        color=Color.blue()
    )
    embed.add_field(name=f"{PREFIX}ping", value="Check bot latency", inline=False)
    embed.add_field(name=f"{PREFIX}help", value="Show this help message", inline=False)
    embed.add_field(name=f"{PREFIX}embed", value="Create a custom embed", inline=False)
    embed.add_field(name=f"{PREFIX}echo <text>", value="Echo back your message", inline=False)
    embed.add_field(name=f"{PREFIX}info", value="Show bot information", inline=False)
    
    await message.reply(embed=embed)


async def cmd_embed(message: Message, args: list):
    """Create a fancy embed"""
    if not args:
        await message.reply(f"Usage: {PREFIX}embed <title> | <description>")
        return
    
    text = " ".join(args)
    if "|" in text:
        title, desc = text.split("|", 1)
        title = title.strip()
        desc = desc.strip()
    else:
        title = "Embed Title"
        desc = text
    
    embed = Embed(
        title=title or "Embed",
        description=desc or "No description",
        color=Color.green()
    )
    embed.set_footer(text=f"Requested by {message.author.display_name}")
    
    await message.reply(embed=embed)


async def cmd_echo(message: Message, args: list):
    """Echo back the user's message"""
    if not args:
        await message.reply(f"Usage: {PREFIX}echo <message>")
        return
    
    await message.reply(" ".join(args))


async def cmd_info(message: Message, args: list):
    """Show bot information"""
    embed = Embed(
        title="🤖 Bot Information",
        color=Color.gold()
    )
    embed.add_field(name="User", value=str(client.user), inline=True)
    embed.add_field(name="ID", value=str(client.user.id), inline=True)
    embed.add_field(name="Guilds", value=str(len(client.guilds)), inline=True)
    embed.add_field(name="Latency", value=f"{round(client.latency * 1000)}ms", inline=True)
    
    await message.reply(embed=embed)


# --- Main Entry Point ---

def main():
    if not BOT_TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN environment variable not set!")
        print("Run: export DISCORD_BOT_TOKEN='your-token-here'")
        return
    
    logger.info("Starting Discord bot...")
    client.run(BOT_TOKEN)


if __name__ == "__main__":
    main()
