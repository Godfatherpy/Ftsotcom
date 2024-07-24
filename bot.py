from aiohttp import web
from plugins import web_server
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime
import asyncio
from pyrogram import filters
import os

# Load AUTO_DELETE_TIME from environment variables with a default of 3600 seconds
AUTO_DELETE_TIME = int(os.getenv('AUTO_DELETE_TIME', 3600))  # 1 hour default

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        if FORCE_SUB_CHANNEL:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                self.invitelink = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning("Bot can't Export Invite link from Force Sub Channel!")
                self.LOGGER(__name__).warning(f"Please Double check the FORCE_SUB_CHANNEL value and Make sure Bot is Admin in channel with Invite Users via Link Permission, Current Force Sub Channel Value: {FORCE_SUB_CHANNEL}")
                self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/codeflix_bots for support")
                sys.exit()

        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="bot working...")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(f"Make Sure bot is Admin in DB Channel, and Double check the CHANNEL_ID Value, Current Value {CHANNEL_ID}")
            self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/codeflix_bots for support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/codeflix_bots")
        self.LOGGER(__name__).info(f""" \n\n

        async def auto_delete_message(client, message, delay: int):
            await asyncio.sleep(delay)
            try:
                await message.delete()
                self.LOGGER(__name__).info(f"Deleted file message: {message.document.file_name}")
            except Exception as e:
                self.LOGGER(__name__).warning(f"Failed to delete message: {e}")

        BOT DEPLOYED BY  @CODEFLIX_BOTS
        """)

        self.username = usr_bot_me.username

        # Web-response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

        # Add handler for document messages
        self.add_handler(filters.document, self.handle_file)

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

    async def handle_file(self, client, message):
        # Notify user about auto-deletion
        await message.reply_text(f"This file will be automatically deleted after {AUTO_DELETE_TIME / 60} minutes.")

        # Save the message ID for later deletion
        self.LOGGER(__name__).info(f"File received: {message.document.file_name}")

        # Schedule the file deletion
        asyncio.create_task(self.auto_delete_message(client, message, AUTO_DELETE_TIME))

    async def auto_delete_message(self, client, message, delay: int):
        await asyncio.sleep(delay)
        try:
            await message.delete()
            self.LOGGER(__name__).info(f"Deleted file message: {message.document.file_name}")
        except Exception as e:
            self.LOGGER(__name__).warning(f"Failed to delete message: {e}")
