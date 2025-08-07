import asyncio
import re
import ast
import math
import logging
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty

from Script import script
from utils import get_shortlink, admin_filter, get_size, is_subscribed, get_poster, search_gagala, temp, get_settings
from database.users_chats_db import db
from database.ia_filterdb import get_search_results
from database.filters_mdb import find_filter, get_filters
from database.gfilters_mdb import find_gfilter, get_gfilters
from info import (
    ADMINS, AUTH_CHANNEL, AUTH_GROUPS, BUTTON_LOCK, BUTTON_LOCK_TEXT,
    CUSTOM_FILE_CAPTION, G_FILTER, IMDB_DELET_TIME, IMDB_TEMPLATE, LOG_CHANNEL,
    P_TTI_SHOW_OFF, PM_IMDB, SINGLE_BUTTON, PROTECT_CONTENT, SPELL_CHECK_REPLY,
    SHORT_URL, SHORT_API
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

FILTER_MODE = {}
G_MODE = {}

@Client.on_message(filters.command('autofilter') & filters.group & filters.create(admin_filter))
async def fil_mod(client, message):
    mode_on = ["yes", "on", "true"]
    mode_off = ["no", "off", "false"]
    try:
        args = message.text.split(None, 1)[1].lower()
    except IndexError:
        return await message.reply("Incomplete command.")
    
    m = await message.reply("Setting...")
    if args in mode_on:
        FILTER_MODE[str(message.chat.id)] = "True"
        await m.edit("Autofilter enabled.")
    elif args in mode_off:
        FILTER_MODE[str(message.chat.id)] = "False"
        await m.edit("Autofilter disabled.")
    else:
        await m.edit("Use `/autofilter on` or `/autofilter off`")

@Client.on_message(filters.group & filters.text & filters.incoming & filters.chat(AUTH_GROUPS) if AUTH_GROUPS else filters.text & filters.incoming & filters.group)
async def give_filter(client, message):
    if G_FILTER and G_MODE.get(str(message.chat.id)) != "False":
        if await global_filters(client, message):
            return

    if await manual_filters(client, message):
        return

    if FILTER_MODE.get(str(message.chat.id)) != "False":
        await auto_filter(client, message)

async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        if message.text.startswith("/"): return
        if re.findall(r"((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if not (2 < len(message.text) < 100):
            return

        search = message.text
        await db.log_search(search)
        files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
        if not files:
            # Log the request if no files are found
            await db.add_request(message.chat.id, message.from_user.id, search)
            if LOG_CHANNEL:
                try:
                    await message.forward(LOG_CHANNEL)
                except Exception as e:
                    logger.error(f"Failed to forward request to log channel: {e}")
            
            if settings["spell_check"]:
                return await advantage_spell_chok(msg)
            return
    else:
        settings = await get_settings(msg.message.chat.id)
        message = msg.message.reply_to_message
        search, files, offset, total_results = spoll
    
    pre = 'filep' if settings['file_secure'] else 'file'
    req = message.from_user.id if message.from_user else 0

    btn = []
    if SHORT_URL and SHORT_API:
        if settings["button"]:
            btn = [[InlineKeyboardButton(f"[{get_size(file.file_size)}] {file.file_name}", url=await get_shortlink(f"https://telegram.dog/{temp.U_NAME}?start=files_{file.file_id}"))] for file in files]
        else:
            btn = [[InlineKeyboardButton(f"{file.file_name}", url=await get_shortlink(f"https://telegram.dog/{temp.U_NAME}?start=files_{file.file_id}")),
                    InlineKeyboardButton(f"{get_size(file.file_size)}", url=await get_shortlink(f"https://telegram.dog/{temp.U_NAME}?start=files_{file.file_id}"))] for file in files]
    else:
        if settings["button"]:
            btn = [[InlineKeyboardButton(f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'{pre}#{req}#{file.file_id}')] for file in files]
        else:
            btn = [[InlineKeyboardButton(f"{file.file_name}", callback_data=f'{pre}#{req}#{file.file_id}'),
                    InlineKeyboardButton(f"{get_size(file.file_size)}", callback_data=f'{pre}#{req}#{file.file_id}')] for file in files]

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        temp.GP_BUTTONS[key] = search
        btn.append([InlineKeyboardButton(text=f"📄 Pages 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
                    InlineKeyboardButton(text="Next ➡️", callback_data=f"next_{req}_{key}_{offset}")])
    
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    cap = IMDB_TEMPLATE.format(query=search, **imdb) if imdb else f"Here is what I found for your query: {search}"

    if imdb and imdb.get('poster'):
        try:
            sent_message = await message.reply_photo(photo=imdb.get('poster'), caption=cap, reply_markup=InlineKeyboardMarkup(btn))
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            sent_message = await message.reply_photo(photo=poster, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
        except Exception as e:
            logger.exception(e)
            sent_message = await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
    else:
        sent_message = await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
    
    await asyncio.sleep(IMDB_DELET_TIME)
    await sent_message.delete()
    try:
        await message.delete()
    except:
        pass

    if spoll:
        await msg.message.delete()

async def advantage_spell_chok(msg):
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE
    )
    query = query.strip() + " movie"
    g_s = await search_gagala(query)
    gs_parsed = []
    if not g_s:
        k = await msg.reply("I couldn't find anything related to that.")
        await asyncio.sleep(8)
        await k.delete()
        return

    regex = re.compile(r".*(imdb|wikipedia).*", re.IGNORECASE)
    gs = list(filter(regex.match, g_s))
    gs_parsed = [re.sub(r'\b(\-([a-zA-Z-\s])\-\simdb|(\-\s)?imdb|(\-\s)?wikipedia|\(|\)|\-|reviews|full|all|episode(s)?|film|movie|series)', '', i, flags=re.IGNORECASE) for i in gs]
    
    if not gs_parsed:
        reg = re.compile(r"watch(\s[a-zA-Z0-9_\s\-\(\)]*)*\|.*", re.IGNORECASE)
        for mv in g_s:
            match = reg.match(mv)
            if match:
                gs_parsed.append(match.group(1))

    user = msg.from_user.id if msg.from_user else 0
    movielist = []
    gs_parsed = list(dict.fromkeys(gs_parsed))
    if len(gs_parsed) > 3:
        gs_parsed = gs_parsed[:3]
    
    if gs_parsed:
        for mov in gs_parsed:
            imdb_s = await get_poster(mov.strip(), bulk=True)
            if imdb_s:
                movielist += [movie.get('title') for movie in imdb_s]

    movielist += [(re.sub(r'(\-|\(|\)|_)', '', i, flags=re.IGNORECASE)).strip() for i in gs_parsed]
    movielist = list(dict.fromkeys(movielist))
    
    if not movielist:
        k = await msg.reply("I couldn't find anything related to that. Check your spelling.")
        await asyncio.sleep(8)
        await k.delete()
        return

    temp.GP_SPELL[msg.id] = movielist
    btn = [
        [InlineKeyboardButton(text=movie.strip(), callback_data=f"spolling#{user}#{k}")]
        for k, movie in enumerate(movielist)
    ]
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spolling#{user}#close_spellcheck')])
    await msg.reply(
        "I couldn't find anything related to that. Did you mean any of these?",
        reply_markup=InlineKeyboardMarkup(btn)
    )

async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)
            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await client.send_message(group_id, reply_text, disable_web_page_preview=True, reply_to_message_id=reply_id)
                        else:
                            button = eval(btn)
                            await client.send_message(group_id, reply_text, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(button), reply_to_message_id=reply_id)
                    elif btn == "[]":
                        await client.send_cached_media(group_id, fileid, caption=reply_text or "", reply_to_message_id=reply_id)
                    else:
                        button = eval(btn)
                        await message.reply_cached_media(fileid, caption=reply_text or "", reply_markup=InlineKeyboardMarkup(button), reply_to_message_id=reply_id)
                    return True
                except Exception as e:
                    logger.exception(e)
                    return False
    return False

async def global_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_gfilters('gfilters')
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_gfilter('gfilters', keyword)
            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            sent_message = await client.send_message(group_id, reply_text, disable_web_page_preview=True, reply_to_message_id=reply_id)
                        else:
                            button = eval(btn)
                            sent_message = await client.send_message(group_id, reply_text, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(button), reply_to_message_id=reply_id)
                    elif btn == "[]":
                        sent_message = await client.send_cached_media(group_id, fileid, caption=reply_text or "", reply_to_message_id=reply_id)
                    else:
                        button = eval(btn)
                        sent_message = await message.reply_cached_media(fileid, caption=reply_text or "", reply_markup=InlineKeyboardMarkup(button), reply_to_message_id=reply_id)
                    
                    await asyncio.sleep(IMDB_DELET_TIME)
                    await sent_message.delete()
                    try:
                        await message.delete()
                    except:
                        pass
                    return True
                except Exception as e:
                    logger.exception(e)
                    return False
    return False
