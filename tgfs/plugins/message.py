# TG-FileStream
# Copyright (C) 2025 Deekshith SH

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from urllib import parse
import aiohttp # Import aiohttp for making HTTP requests

from telethon import events
from telethon.custom import Message

from tgfs.config import Config
from tgfs.telegram import client
from tgfs.utils import get_filename

log = logging.getLogger(__name__)

SHORTENER_API_URL = "https://senapi-link.vercel.app/link" # Define the shortener API URL

@client.on(events.NewMessage(incoming=True, func=lambda x: x.is_private and not x.file))
async def handle_text_message(evt: events.NewMessage.Event) -> None:
    # Enhanced welcome message
    await evt.reply(
        "👋 **Hello there!**\n\n"
        "✨ Send me any **Telegram file or photo** and I'll generate a super quick download link for you!\n"
        "🚀 Try it now!"
    )

@client.on(events.NewMessage(incoming=True, func=lambda x: x.is_private and x.file))
async def handle_file_message(evt: events.NewMessage.Event) -> None:
    fwd_msg: Message = await evt.message.forward_to(Config.BIN_CHANNEL)
    original_url = f"{Config.PUBLIC_URL}/{fwd_msg.id}/{parse.quote(get_filename(evt))}"
    log.info("Generated Original Link: %s", original_url)

    shortened_url = None
    try:
        async with aiohttp.ClientSession() as session:
            # Make a GET request to the shortener API
            async with session.get(f"{SHORTENER_API_URL}=?link={original_url}") as response:
                response.raise_for_status() # Raise an exception for bad status codes
                data = await response.json()
                shortened_url = data.get("short_url")
                log.info("Shortened Link: %s", shortened_url)
    except aiohttp.ClientError as e:
        log.error("Error shortening URL: %s", e)
        shortened_url = None # Fallback to original if shortening fails
    except Exception as e:
        log.error("An unexpected error occurred during URL shortening: %s", e)
        shortened_url = None

    if shortened_url:
        await evt.reply(
            f"🔗 **Here's your download link:**\n"
            f"`{shortened_url}`\n\n"
            f"⚠️ **Please note:** This link is valid for **30 minutes only** and will expire afterwards."
        )
    else:
        # If shortening failed, send the original link with a warning
        await evt.reply(
            f"🔗 **Here's your download link (shortening failed):**\n"
            f"`{original_url}`\n\n"
            f"⚠️ **Please note:** This link is valid for **30 minutes only** and will expire afterwards."
        )
    log.info("Sent link to user for message ID: %d", evt.message.id)

