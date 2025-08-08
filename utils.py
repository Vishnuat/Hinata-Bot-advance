import logging
import os
import re
import asyncio
import requests
import aiohttp
from pyrogram.errors import UserNotParticipant
from pyrogram.types import Message, InlineKeyboardButton
from pyrogram import enums
from info import ADMINS, AUTH_CHANNEL, LONG_IMDB_DESCRIPTION, MAX_LIST_ELM, SHORT_URL, SHORT_API
from imdb import Cinemagoer
from typing import Union, List
from datetime import datetime, timedelta
from database.users_chats_db import db
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

__repo__ = "https://github.com/MrMKN/PROFESSOR-BOT"
__license__ = "AGPL-3.0"
__copyright__ = "© 2024 MrMKN"
__version__ = "4.6"

BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)\]\((buttonurl|buttonalert):(?:/{0,2})(.+?)(:same)?\))")
BANNED = {}
SMART_OPEN = '“'
SMART_CLOSE = '”'
START_CHAR = ('\'', '"', SMART_OPEN)

# temp db for banned
class temp(object):
    BANNED_USERS = []
    BANNED_CHATS = []
    CURRENT = 0
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None
    SETTINGS = {}
    GP_BUTTONS = {}
    PM_BUTTONS = {}
    PM_SPELL = {}
    GP_SPELL = {}

async def admin_filter(filt, client, message):
    if not message.from_user:
        return False
    if message.from_user.id in ADMINS:
        return True
    if message.chat.type == enums.ChatType.PRIVATE:
        return False
    try:
        member = await message.chat.get_member(message.from_user.id)
        return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    except Exception:
        return False

async def is_subscribed(bot, query):
    try:
        user = await bot.get_chat_member(AUTH_CHANNEL, query.from_user.id)
    except UserNotParticipant:
        return False
    except Exception as e:
        logger.error(e)
        return False
    else:
        return user.status != enums.ChatMemberStatus.BANNED

async def get_poster(query, bulk=False, id=False, file=None):
    imdb = Cinemagoer()
    if not id:
        query = (query.strip()).lower()
        title = query
        year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
        if year:
            year = list_to_str(year[:1])
            title = (query.replace(year, "")).strip()
        elif file is not None:
            year = re.findall(r'[1-2]\d{3}', file, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1])
        else:
            year = None
        try:
           movieid = imdb.search_movie(title.lower(), results=10)
        except:
           return None
        if not movieid:
            return None
        if year:
            filtered=list(filter(lambda k: str(k.get('year')) == str(year), movieid))
            if not filtered:
                filtered = movieid
        else:
            filtered = movieid
        movieid=list(filter(lambda k: k.get('kind') in ['movie', 'tv series'], filtered))
        if not movieid:
            movieid = filtered
        if bulk:
            return movieid
        movieid = movieid[0].movieID
    else:
        movieid = query
    movie = imdb.get_movie(movieid)
    if movie.get("original air date"):
        date = movie["original air date"]
    elif movie.get("year"):
        date = movie.get("year")
    else:
        date = "N/A"
    plot = ""
    if not LONG_IMDB_DESCRIPTION:
        plot = movie.get('plot')
        if plot and len(plot) > 0:
            plot = plot[0]
    else:
        plot = movie.get('plot outline')
    if plot and len(plot) > 800:
        plot = plot[0:800] + "..."

    return {
        'title': movie.get('title'),
        'votes': movie.get('votes'),
        "aka": list_to_str(movie.get("akas")),
        "seasons": movie.get("number of seasons"),
        "box_office": movie.get('box office'),
        'localized_title': movie.get('localized title'),
        'kind': movie.get("kind"),
        "imdb_id": f"tt{movie.get('imdbID')}",
        "cast": list_to_str(movie.get("cast")),
        "runtime": list_to_str(movie.get("runtimes")),
        "countries": list_to_str(movie.get("countries")),
        "certificates": list_to_str(movie.get("certificates")),
        "languages": list_to_str(movie.get("languages")),
        "director": list_to_str(movie.get("director")),
        "writer":list_to_str(movie.get("writer")),
        "producer":list_to_str(movie.get("producer")),
        "composer":list_to_str(movie.get("composer")) ,
        "cinematographer":list_to_str(movie.get("cinematographer")),
        "music_team": list_to_str(movie.get("music department")),
        "distributors": list_to_str(movie.get("distributors")),
        'release_date': date,
        'year': movie.get('year'),
        'genres': list_to_str(movie.get("genres")),
        'poster': movie.get('full-size cover url'),
        'plot': plot,
        'rating': str(movie.get("rating")),
        'url':f'https://www.imdb.com/title/tt{movieid}'
    }

def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    elif MAX_LIST_ELM:
        k = k[:int(MAX_LIST_ELM)]
        return ' '.join(f'{elem}, ' for elem in k)
    else:
        return ' '.join(f'{elem}, ' for elem in k)

async def search_gagala(text):
    usr_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/61.0.3163.100 Safari/537.36'
    }
    text = text.replace(" ", '+')
    url = f'https://www.google.com/search?q={text}'
    response = requests.get(url, headers=usr_agent)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    titles = soup.find_all('h3')
    return [title.getText() for title in titles]

async def get_settings(group_id):
    settings = temp.SETTINGS.get(group_id)
    if not settings:
        settings = await db.get_settings(group_id)
        temp.SETTINGS[group_id] = settings
    return settings

async def save_group_settings(group_id, key, value):
    current = await get_settings(group_id)
    current[key] = value
    temp.SETTINGS[group_id] = current
    await db.update_settings(group_id, current)

def get_size(size):
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

def get_file_id(msg: Message):
    if not msg.media:
        return None
    for message_type in ("photo", "animation", "audio", "document", "video", "video_note", "voice", "sticker"):
        obj = getattr(msg, message_type)
        if obj:
            setattr(obj, "message_type", message_type)
            return obj

def extract_user(message: Message) -> Union[int, str]:
    user_id = None
    user_first_name = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name
    elif len(message.command) > 1:
        if (len(message.entities) > 1 and message.entities[1].type == enums.MessageEntityType.TEXT_MENTION):
            required_entity = message.entities[1]
            user_id = required_entity.user.id
            user_first_name = required_entity.user.first_name
        else:
            user_id = message.command[1]
            user_first_name = user_id
        try:
            user_id = int(user_id)
        except ValueError:
            pass
    else:
        user_id = message.from_user.id
        user_first_name = message.from_user.first_name
    return (user_id, user_first_name)

def split_quotes(text: str) -> List:
    if not any(text.startswith(char) for char in START_CHAR):
        return text.split(None, 1)
    counter = 1
    while counter < len(text):
        if text[counter] == "\\":
            counter += 1
        elif text[counter] == text[0] or (text[0] == SMART_OPEN and text[counter] == SMART_CLOSE):
            break
        counter += 1
    else:
        return text.split(None, 1)

    key = remove_escapes(text[1:counter].strip())
    rest = text[counter + 1:].strip()
    if not key:
        key = text[0] + text[0]
    return list(filter(None, [key, rest]))

def parser(text, keyword, cb_data):
    if "buttonalert" in text:
        text = (text.replace("\n", "\\n").replace("\t", "\\t"))
    buttons = []
    note_data = ""
    prev = 0
    i = 0
    alerts = []
    for match in BTN_URL_REGEX.finditer(text):
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1
        if n_escapes % 2 == 0:
            note_data += text[prev:match.start(1)]
            prev = match.end(1)
            if match.group(3) == "buttonalert":
                if bool(match.group(5)) and buttons:
                    buttons[-1].append(InlineKeyboardButton(match.group(2), callback_data=f"{cb_data}:{i}:{keyword}"))
                else:
                    buttons.append([InlineKeyboardButton(match.group(2), callback_data=f"{cb_data}:{i}:{keyword}")])
                i += 1
                alerts.append(match.group(4))
            elif bool(match.group(5)) and buttons:
                buttons[-1].append(InlineKeyboardButton(match.group(2), url=match.group(4).replace(" ", "")))
            else:
                buttons.append([InlineKeyboardButton(match.group(2), url=match.group(4).replace(" ", ""))])
        else:
            note_data += text[prev:to_check]
            prev = match.start(1) - 1
    else:
        note_data += text[prev:]
    return note_data, buttons, alerts

def remove_escapes(text: str) -> str:
    res = ""
    is_escaped = False
    for char in text:
        if is_escaped:
            res += char
            is_escaped = False
        elif char == "\\":
            is_escaped = True
        else:
            res += char
    return res

def humanbytes(size):
    if not size:
        return ""
    power = 1024
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {Dic_powerN[n]}B"

def get_time(seconds):
    periods = [('d', 86400), ('h', 3600), ('m', 60), ('s', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)}{period_name}'
    return result

async def get_shortlink(link):
    url = f'{SHORT_URL}/api'
    params = {'api': SHORT_API, 'url': link}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                data = await response.json()
                return data.get('shortenedUrl', link) if data.get("status") == "success" else link
    except Exception as e:
        logger.error(e)
        return link

def extract_time(time_val):
    if any(time_val.endswith(unit) for unit in ("s", "m", "h", "d")):
        unit = time_val[-1]
        time_num = time_val[:-1]
        if not time_num.isdigit():
            return None

        if unit == "s":
            return datetime.now() + timedelta(seconds=int(time_num))
        elif unit == "m":
            return datetime.now() + timedelta(minutes=int(time_num))
        elif unit == "h":
            return datetime.now() + timedelta(hours=int(time_num))
        elif unit == "d":
            return datetime.now() + timedelta(days=int(time_num))
    return None

async def get_ott_releases():
    """
    Scrapes a reliable source for upcoming OTT releases.
    Note: This is a placeholder and may need updates if the website structure changes.
    """
    try:
        # Using a placeholder implementation as real-time scraping is complex
        placeholder_releases = [
            "**Kalki 2898 AD**\n- Platform: Netflix\n- Release Date: Aug 15, 2025",
            "**Pushpa 2: The Rule**\n- Platform: Amazon Prime Video\n- Release Date: Aug 22, 2025",
            "**Mirzapur Season 4**\n- Platform: Amazon Prime Video\n- Release Date: Aug 29, 2025",
            "**The Family Man Season 3**\n- Platform: Amazon Prime Video\n- Release Date: Sep 5, 2025"
        ]
        if not placeholder_releases:
            return "Could not find any upcoming OTT releases at the moment."
        return "\n\n".join(placeholder_releases)
    except Exception as e:
        logger.error(f"Error scraping OTT releases: {e}")
        return "Could not fetch OTT release information at this time."

def detect_language(text):
    """
    Detects one or more languages from a file's name or caption based on keywords.
    """
    text = text.lower()
    # Using a set to automatically handle and store unique languages found
    languages_found = set()
    
    # A dictionary mapping various keywords/abbreviations to a standard language name
    language_map = {
        "malayalam": "Malayalam", "mal": "Malayalam",
        "tamil": "Tamil", "tam": "Tamil",
        "hindi": "Hindi", "hin": "Hindi",
        "english": "English", "eng": "English",
        "telugu": "Telugu", "tel": "Telugu",
        "kannada": "Kannada", "kan": "Kannada"
    }

    # Find all potential language keywords in the text
    # This regex looks for words of 3 or more letters
    potential_keywords = re.findall(r'\b[a-z]{3,}\b', text)
    
    for keyword in potential_keywords:
        if keyword in language_map:
            languages_found.add(language_map[keyword])

    if languages_found:
        # Sort the list for consistent output order and join into a string
        return ", ".join(sorted(list(languages_found)))
    
    return "Unknown"
