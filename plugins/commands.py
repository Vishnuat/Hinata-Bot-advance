import os
import re
import json
import base64
import logging
import random
import asyncio
from urllib.parse import unquote_plus
from plugins.pm_filter import pm_AutoFilter

from Script import script
from database.users_chats_db import db
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from info import CHANNELS, ADMINS, AUTH_CHANNEL, LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT, START_MESSAGE, FORCE_SUB_TEXT, SUPPORT_CHAT
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp
from database.connections_mdb import active_connection

logger = logging.getLogger(__name__)
BATCH_FILES = {}

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [InlineKeyboardButton('📢 Updates', url=f'https://t.me/{SUPPORT_CHAT}'),
             InlineKeyboardButton('ℹ️ Help', url=f"https://t.me/{temp.U_NAME}?start=help")]
        ]
        await message.reply(
            START_MESSAGE.format(user=message.from_user.mention if message.from_user else message.chat.title, bot=client.mention),
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(a=message.chat.title, b=message.chat.id, c=message.chat.username, d=total, f=client.mention, e="Unknown"))
            await db.add_chat(message.chat.id, message.chat.title, message.chat.username)
        return

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention, message.from_user.username, temp.U_NAME))

    if len(message.command) != 2:
        buttons = [
            [InlineKeyboardButton("➕ Add Me To Your Group ➕", url=f"http://t.me/{temp.U_NAME}?startgroup=true")],
            [InlineKeyboardButton("🔍 Search", switch_inline_query_current_chat=''),
             InlineKeyboardButton("📢 Updates", url="https://t.me/mkn_bots_updates")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help"),
             InlineKeyboardButton("✨ About", callback_data="about")]
        ]
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=START_MESSAGE.format(user=message.from_user.mention, bot=client.mention),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    data = message.command[1]
    
    # Handle search from update channel
    if data.startswith("search_"):
        query = unquote_plus(data.split("_", 1)[1])
        # To reuse pm_AutoFilter, we can modify the message object in-place
        message.text = query
        await pm_AutoFilter(client, message)
        return

    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("Make sure the bot is an admin in the force-subscribe channel.")
            return
        btn = [
            [InlineKeyboardButton("✨ Join My Channel ✨", url=invite_link.invite_link)],
        ]
        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub'
                btn.append([InlineKeyboardButton("🔄 Try Again", callback_data=f"{pre}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton("🔄 Try Again", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
        await client.send_message(
            chat_id=message.from_user.id,
            text=FORCE_SUB_TEXT,
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return

    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [
            [InlineKeyboardButton("➕ Add Me To Your Group ➕", url=f"http://t.me/{temp.U_NAME}?startgroup=true")],
            [InlineKeyboardButton("🔍 Search", switch_inline_query_current_chat=''),
             InlineKeyboardButton("📢 Updates", url="https://t.me/mkn_bots_updates")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help"),
             InlineKeyboardButton("✨ About", callback_data="about")]
        ]
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=START_MESSAGE.format(user=message.from_user.mention, bot=client.mention),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""

    if data.split("-", 1)[0] == "BATCH":
        sts = await message.reply("Please wait...")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            try:
                file = await client.download_media(file_id)
                with open(file) as file_data:
                    msgs = json.loads(file_data.read())
            except Exception:
                await sts.edit("Failed to process the batch file.")
                return
            finally:
                if os.path.exists(file):
                    os.remove(file)
            BATCH_FILES[file_id] = msgs

        for msg in msgs:
            title = msg.get("title")
            size = get_size(int(msg.get("size", 0)))
            f_caption = msg.get("caption", "")
            if BATCH_FILE_CAPTION:
                try:
                    f_caption = BATCH_FILE_CAPTION.format(
                        mention=message.from_user.mention,
                        file_name=title or '',
                        file_size=size or '',
                        file_caption=f_caption or ''
                    )
                except Exception as e:
                    logger.exception(e)

            try:
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption or title,
                    protect_content=msg.get('protect', False)
                )
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption or title,
                    protect_content=msg.get('protect', False)
                )
            except Exception as e:
                logger.warning(e, exc_info=True)
                continue
            await asyncio.sleep(1)
        await sts.delete()
        return

    files_ = await get_file_details(file_id)
    if not files_:
        try:
            pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=pre == 'filep'
            )
            file_type = msg.media
            file = getattr(msg, file_type)
            title = file.file_name
            size = get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(
                        mention=message.from_user.mention,
                        file_name=title or '',
                        file_size=size or '',
                        file_caption=''
                    )
                except Exception:
                    pass
            await msg.edit_caption(f_caption)
            return
        except Exception:
            pass
        return await message.reply('No such file exists!')

    files = files_[0]
    title = files.file_name
    size = get_size(files.file_size)
    f_caption = files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption = CUSTOM_FILE_CAPTION.format(
                mention=message.from_user.mention,
                file_name=title or '',
                file_size=size or '',
                file_caption=f_caption or ''
            )
        except Exception as e:
            logger.exception(e)

    await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption or title,
        protect_content=pre == 'filep'
    )
