import asyncio
import ast
import time
import math
import logging
import random
import shutil
import psutil

from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto

from Script import script
from utils import get_size, is_subscribed, get_poster, temp, get_settings, save_group_settings, get_shortlink, get_time, humanbytes
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, make_inactive
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import del_all, find_filter
from database.gfilters_mdb import find_gfilter
from database.users_chats_db import db
from info import ADMINS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION, PICS, IMDB_TEMPLATE, IMDB_DELET_TIME, BUTTON_LOCK, BUTTON_LOCK_TEXT, SHORT_URL, SHORT_API

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    """
    Handles all callback queries for the bot.
    """
    if query.data == "close_data":
        await query.message.delete()
        return

    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grp_id = await active_connecticonnectionon(str(userid))
            if not grp_id:
                return await query.message.edit_text("I'm not connected to any groups!")
            try:
                chat = await client.get_chat(grp_id)
                title = chat.title
            except Exception:
                return await query.message.edit_text("Make sure I'm present in your group!")
        else:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        st = await client.get_chat_member(grp_id, userid)
        if st.status == enums.ChatMemberStatus.OWNER or str(userid) in ADMINS:
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be the group owner to do that!", show_alert=True)
        return

    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if st.status == enums.ChatMemberStatus.OWNER or str(userid) in ADMINS:
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except Exception:
                    pass
            else:
                await query.answer("Don't touch others' property!", show_alert=True)
        else:
            await query.message.delete()
        return

    elif "groupcb" in query.data:
        group_id, act = query.data.split(":")[1:]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        
        stat, cb = ("Connect", "connectcb") if act == "" else ("Disconnect", "disconnect")
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(stat, callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("Delete", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("Back", callback_data="backcb")]
        ])
        await query.message.edit_text(f"Group Name: **{title}**\nGroup ID: `{group_id}`", reply_markup=keyboard)
        return

    elif "connectcb" in query.data:
        group_id = query.data.split(":")[1]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        
        if await make_active(str(query.from_user.id), str(group_id)):
            await query.message.edit_text(f"Connected to: **{title}**")
        else:
            await query.message.edit_text('Some error occurred!')
        return

    elif "disconnect" in query.data:
        group_id = query.data.split(":")[1]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        
        if await make_inactive(str(query.from_user.id)):
            await query.message.edit_text(f"Disconnected from **{title}**")
        else:
            await query.message.edit_text("Some error occurred!")
        return

    elif "deletecb" in query.data:
        group_id = query.data.split(":")[1]
        if await delete_connection(str(query.from_user.id), str(group_id)):
            await query.message.edit_text("Successfully deleted connection.")
        else:
            await query.message.edit_text("Some error occurred!")
        return

    elif query.data == "backcb":
        groupids = await all_connections(str(query.from_user.id))
        if not groupids:
            return await query.message.edit_text("There are no active connections!")
        
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(query.from_user.id), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append([InlineKeyboardButton(f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}")])
            except Exception:
                pass
        
        if buttons:
            await query.message.edit_text("Your connected group details:", reply_markup=InlineKeyboardMarkup(buttons))
        return

    elif "alertmessage" in query.data:
        _, i, keyword = query.data.split(":")
        reply_text, btn, alerts, fileid = await find_filter(query.message.chat.id, keyword)
        if alerts:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)].replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
        return

    elif "galert" in query.data:
        _, i, keyword = query.data.split(":")
        reply_text, btn, alerts, fileid = await find_gfilter("gfilters", keyword)
        if alerts:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)].replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
        return

    if query.data.startswith("pmfile"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exists.')
        
        file = files_[0]
        title = file.file_name
        size = get_size(file.file_size)
        f_caption = CUSTOM_FILE_CAPTION.format(
            mention=query.from_user.mention,
            file_name=title,
            file_size=size,
            file_caption=file.caption or ""
        ) if CUSTOM_FILE_CAPTION else title

        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                return await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
            
            await client.send_cached_media(
                chat_id=query.from_user.id,
                file_id=file_id,
                caption=f_caption,
                protect_content=ident == "pmfilep"
            )
        except Exception as e:
            await query.answer(f"⚠️ Error: {e}", show_alert=True)
        return

    if query.data.startswith("file"):
        ident, req, file_id = query.data.split("#")
        if BUTTON_LOCK and int(req) != query.from_user.id and int(req) != 0:
            return await query.answer(BUTTON_LOCK_TEXT.format(query=query.from_user.first_name), show_alert=True)

        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exists.')

        file = files_[0]
        title = file.file_name
        size = get_size(file.file_size)
        settings = await get_settings(query.message.chat.id)
        f_caption = CUSTOM_FILE_CAPTION.format(
            mention=query.from_user.mention,
            file_name=title,
            file_size=size,
            file_caption=file.caption or ""
        ) if CUSTOM_FILE_CAPTION else title

        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                return await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
            
            if settings['botpm']:
                return await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
            
            await client.send_cached_media(
                chat_id=query.from_user.id,
                file_id=file_id,
                caption=f_caption,
                protect_content=ident == "filep"
            )
            await query.answer('Check your PM, I have sent the files there.', show_alert=True)
        except UserIsBlocked:
            await query.answer('Unblock the bot first!', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        return

    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            return await query.answer("Don't be oversmart!", show_alert=True)
        
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exists.')
        
        file = files_[0]
        title = file.file_name
        size = get_size(file.file_size)
        f_caption = CUSTOM_FILE_CAPTION.format(
            mention=query.from_user.mention,
            file_name=title,
            file_size=size,
            file_caption=file.caption or ""
        ) if CUSTOM_FILE_CAPTION else title
        
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=ident == 'checksubp'
        )
        return

    elif query.data == "pages":
        await query.answer("Curiosity is a little more, isn't it?", show_alert=True)
        return

    elif query.data == "howdl":
        await query.answer(script.HOW_TO_DOWNLOAD.format(query.from_user.first_name), show_alert=True)
        return

    elif query.data == "start":
        buttons = [
            [InlineKeyboardButton("➕️ Add Me To Your Chat ➕", url=f"http://t.me/{temp.U_NAME}?startgroup=true")],
            [InlineKeyboardButton("Search 🔎", switch_inline_query_current_chat=''),
             InlineKeyboardButton("Channel 🔈", url="https://t.me/mkn_bots_updates")],
            [InlineKeyboardButton("Help 🕸️", callback_data="help"),
             InlineKeyboardButton("About ✨", callback_data="about")]
        ]
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.START_TXT.format(user=query.from_user.mention, bot=client.mention)),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    elif query.data == "help":
        buttons = [
            [InlineKeyboardButton('⚙️ Admin Panel ⚙️', 'admin')],
            [InlineKeyboardButton('Filters', 'openfilter'),
             InlineKeyboardButton('Connect', 'coct')],
            [InlineKeyboardButton('File Store', 'newdata'),
             InlineKeyboardButton('Extra Mode', 'extmod')],
            [InlineKeyboardButton('Group Manager', 'gpmanager'),
             InlineKeyboardButton('Bot Status ❄️', 'stats')],
            [InlineKeyboardButton('✘ Close', 'close_data'),
             InlineKeyboardButton('« Back', 'start')]
        ]
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.HELP_TXT.format(query.from_user.mention)),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    elif query.data == "about":
        buttons = [
            [InlineKeyboardButton('Source Code 📜', 'source')],
            [InlineKeyboardButton('✘ Close', 'close_data'),
             InlineKeyboardButton('« Back', 'start')]
        ]
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.ABOUT_TXT.format(temp.B_NAME)),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    elif query.data == "source":
        buttons = [
            [InlineKeyboardButton('Source Code', url='https://github.com/MrMKN/PROFESSOR-BOT')],
            [InlineKeyboardButton('‹ Back', 'about')]
        ]
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.SOURCE_TXT),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    elif query.data == "admin":
        if query.from_user.id not in ADMINS:
            return await query.answer("This menu is only for my admins.", show_alert=True)
        
        total, used, free = shutil.disk_usage(".")
        stats = script.SERVER_STATS.format(
            get_time(time.time() - client.uptime),
            psutil.cpu_percent(),
            psutil.virtual_memory().percent,
            humanbytes(total),
            humanbytes(used),
            psutil.disk_usage('/').percent,
            humanbytes(free)
        )
        
        buttons = [
            [InlineKeyboardButton('✘ Close', 'close_data'),
             InlineKeyboardButton('« Back', 'help')]
        ]
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.ADMIN_TXT),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    elif query.data == "stats":
        buttons = [
            [InlineKeyboardButton('⟳ Refresh', 'stats'),
             InlineKeyboardButton('« Back', 'help')]
        ]
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.STATUS_TXT.format(total, users, chats, get_size(monsize), get_size(free))),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))
        if str(grp_id) != str(grpid):
            return await query.message.edit("Your active connection has been changed. Go to /settings")
        
        await save_group_settings(grpid, set_type, status == "False")
        settings = await get_settings(grpid)
        
        buttons = [
            [InlineKeyboardButton(f"Filter Button: {'Single' if settings['button'] else 'Double'}", f'setgs#button#{settings["button"]}#{grp_id}')],
            [InlineKeyboardButton(f"File in PM: {'On' if settings['botpm'] else 'Off'}", f'setgs#botpm#{settings["botpm"]}#{grp_id}')],
            [InlineKeyboardButton(f"Restrict Content: {'On' if settings['file_secure'] else 'Off'}", f'setgs#file_secure#{settings["file_secure"]}#{grp_id}')],
            [InlineKeyboardButton(f"IMDB in Filter: {'On' if settings['imdb'] else 'Off'}", f'setgs#imdb#{settings["imdb"]}#{grp_id}')],
            [InlineKeyboardButton(f"Spelling Check: {'On' if settings['spell_check'] else 'Off'}", f'setgs#spell_check#{settings["spell_check"]}#{grp_id}')],
            [InlineKeyboardButton(f"Welcome Message: {'On' if settings['welcome'] else 'Off'}", f'setgs#welcome#{settings["welcome"]}#{grp_id}')]
        ]
        await query.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
        return
