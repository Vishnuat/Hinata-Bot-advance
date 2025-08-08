"""
This is the main entry point for the Telegram bot. It initializes the bot,
sets up logging, and starts the client.
"""

import os
import asyncio
import logging
import logging.config
import datetime
import pytz
from aiohttp import web
from pyrogram import Client, types
from database.users_chats_db import db
from database.ia_filterdb import Media
from utils import temp, __repo__, __license__, __copyright__, __version__
from info import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, UPTIME, WEB_SUPPORT

# --- LOGGING SETUP ---
logging.config.fileConfig("logging.conf")
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("cinemagoer").setLevel(logging.ERROR)

class Bot(Client):
    """
    A custom Pyrogram client for the Telegram bot.
    """
    def __init__(self):
        super().__init__(
            name="Professor-Bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins={"root": "plugins"}
        )

    async def start(self):
        """
        Initializes the bot and starts the client.
        """
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats

        await super().start()
        await Media.ensure_indexes()

        me = await self.get_me()
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.id = me.id
        self.name = me.first_name
        self.mention = me.mention
        self.username = me.username
        self.log_channel = LOG_CHANNEL
        self.uptime = UPTIME

        curr = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        date = curr.strftime('%d %B, %Y')
        time = curr.strftime('%I:%M:%S %p')
        
        log_message = (
            f"{me.first_name} Iꜱ Rᴇsᴛᴀʀᴛᴇᴅ....✨\n\n"
            f"🗓️ Dᴀᴛᴇ : {date}\n"
            f"⏰ Tɪᴍᴇ : {time}\n\n"
            f"🖥️ Rᴇᴩᴏ: {__repo__}\n"
            f"🉐 Vᴇʀsɪᴏɴ: {__version__}\n"
            f"🧾 Lɪᴄᴇɴꜱᴇ: {__license__}\n"
            f"©️ Cᴏᴩʏʀɪɢʜᴛ: {__copyright__}"
        )
        
        logging.info(log_message)
        
        try:
            await self.send_message(LOG_CHANNEL, text=log_message, disable_web_page_preview=True)
        except Exception as e:
            logging.warning(f"Bot Isn't Able To Send Message To LOG_CHANNEL: {e}")
        
        if WEB_SUPPORT:
            app = web.AppRunner(web.Application(client_max_size=30000000))
            await app.setup()
            await web.TCPSite(app, "0.0.0.0", 8080).start()
            logging.info("Web Response Is Running......🕸️")

    async def stop(self, *args):
        """
        Stops the bot gracefully.
        """
        await super().stop()
        logging.info("Bot Is Restarting ⟳...")

    async def iter_messages(
        self,
        chat_id: int | str,
        limit: int,
        offset: int = 0
    ) -> types.Message | None:
        """
        Iterates through messages in a chat.
        """
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current + new_diff + 1)))
            for message in messages:
                yield message
                current += 1

if __name__ == "__main__":
    Bot().run()
