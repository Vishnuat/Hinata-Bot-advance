"""
This script centralizes all configuration variables and text strings for the bot,
making it easier to manage settings and user-facing messages.
"""
import re
import time
from os import environ

id_pattern = re.compile(r'^.\d+$')

def is_enabled(value, default):
    """
    Checks if a configuration value is enabled.
    """
    if value.strip().lower() in ["on", "true", "yes", "1", "enable", "y"]:
        return True
    elif value.strip().lower() in ["off", "false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# --- PYROCLIENT SETUP ---
API_ID = int(environ['API_ID'])
API_HASH = environ['API_HASH']
BOT_TOKEN = environ['BOT_TOKEN']

# --- BOT SETTINGS ---
WEB_SUPPORT = is_enabled(environ.get("WEBHOOK", 'True'), True)
PICS = (environ.get('PICS', 'https://graph.org/file/01ddfcb1e8203879a63d7.jpg https://graph.org/file/d69995d9846fd4ad632b8.jpg')).split()
UPTIME = time.time()

# --- ADMINS, CHANNELS & USERS ---
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '0').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
AUTH_CHANNEL = int(auth_channel) if (auth_channel := environ.get('AUTH_CHANNEL')) and id_pattern.search(auth_channel) else None
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if (auth_grp := environ.get('AUTH_GROUP')) else None

# --- MONGODB INFORMATION ---
DATABASE_URL = environ.get('DATABASE_URL', "")
DATABASE_NAME = environ.get('DATABASE_NAME', "Cluster0")
FILE_DB_URL = environ.get("FILE_DB_URL", DATABASE_URL)
FILE_DB_NAME = environ.get("FILE_DB_NAME", DATABASE_NAME)
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Telegram_files')

# --- FILTERS CONFIGURATION ---
MAX_RIST_BTNS = int(environ.get('MAX_RIST_BTNS', 10))
BUTTON_LOCK = is_enabled(environ.get("BUTTON_LOCK", "True"), True)
PMFILTER = is_enabled(environ.get('PMFILTER', "True"), True)
G_FILTER = is_enabled(environ.get("G_FILTER", "True"), True)

# --- URL SHORTENER ---
SHORT_URL = environ.get("SHORT_URL")
SHORT_API = environ.get("SHORT_API")

# --- OTHERS ---
IMDB_DELET_TIME = int(environ.get('IMDB_DELET_TIME', 300))
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', 0))
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'MKN_BOTZ_DISCUSSION_GROUP')
P_TTI_SHOW_OFF = is_enabled(environ.get('P_TTI_SHOW_OFF', "True"), True)
PM_IMDB = is_enabled(environ.get('PM_IMDB', "True"), True)
IMDB = is_enabled(environ.get('IMDB', "True"), True)
SINGLE_BUTTON = is_enabled(environ.get('SINGLE_BUTTON', "True"), True)
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", "{file_name}")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION")
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "True"), True)
MAX_LIST_ELM = int(environ.get("MAX_LIST_ELM", 0))
FILE_STORE_CHANNEL = [int(ch) for ch in environ.get('FILE_STORE_CHANNEL', '').split()]
MELCOW_NEW_USERS = is_enabled(environ.get('MELCOW_NEW_USERS', "True"), True)
PROTECT_CONTENT = is_enabled(environ.get('PROTECT_CONTENT', "False"), False)
PUBLIC_FILE_STORE = is_enabled(environ.get('PUBLIC_FILE_STORE', "True"), True)

class Text:
    START_TXT = "<b>✨ Hᴇʟʟᴏ {user}.\n\nMʏ Nᴀᴍᴇ Is {bot}.\n\nI Cᴀɴ Pʀᴏᴠɪᴅᴇ Mᴏᴠɪᴇs Fᴏʀ Yᴏᴜ. Jᴜsᴛ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ Oʀ Jᴏɪɴ Oᴜʀ Gʀᴏᴜᴘ.</b>"
    HELP_TXT = "Hᴇʏ {}, Hᴇʀᴇ Is Mʏ Hᴇʟᴩ."
    ABOUT_TXT = """<b>✯ Mʏ ɴᴀᴍᴇ: {}
✯ Dᴇᴠᴇʟᴏᴩᴇʀ: <a href="https://t.me/Mr_MKN">ᴍʀ.ᴍᴋɴ ᴛɢ</a>
✯ Cᴏᴅᴇᴅ Oɴ: ᴩʏᴛʜᴏɴ/ᴩʏʀᴏɢʀᴀᴍ
✯ Mʏ DᴀᴛᴀBᴀꜱᴇ: ᴍᴏɴɢᴏ-ᴅʙ
✯ Mʏ Sᴇʀᴠᴇʀ: ᴀɴʏᴡʜᴇʀᴇ
✯ Mʏ Vᴇʀꜱɪᴏɴ: ᴩʀᴏꜰᴇꜱꜱᴏʀ-ʙᴏᴛ ᴠ4.6 (12-05-2025)</b>"""
    SOURCE_TXT = """<b>NOTE:</b>
- ꜱᴏᴜʀᴄᴇ ᴄᴏᴅᴇ ʜᴇʀᴇ ◉› :<a href=https://github.com/MrMKN/PROFESSOR-BOT>𝐏𝐑𝐎𝐅𝐄𝐒𝐒𝐎𝐑-𝐁𝐎𝐓</a>

<b>ᴅᴇᴠ: <a href=https://t.me/Mr_MKN>ᴍʀ.ᴍᴋɴ ᴛɢ</a></b>"""
    FILE_TXT = """<b>➤ Hᴇʟᴘ Fᴏʀ Fɪʟᴇ Sᴛᴏʀᴇ</b>

<i>Bʏ Usɪɴɢ Tʜɪs Mᴏᴅᴜʟᴇ Yᴏᴜ Cᴀɴ Sᴛᴏʀᴇ Fɪʟᴇs Iɴ Mʏ Dᴀᴛᴀʙᴀsᴇ Aɴᴅ I Wɪʟʟ Gɪᴠᴇ Yᴏᴜ A Pᴇʀᴍᴀɴᴇɴᴛ Lɪɴᴋ Tᴏ Aᴄᴄᴇss Tʜᴇ Sᴀᴠᴇᴅ Fɪʟᴇs.</i>

<b>⪼ Cᴏᴍᴍᴀɴᴅ & Usᴀɢᴇ</b>
➪ /link › Rᴇᴘʟʏ Tᴏ Aɴʏ Mᴇᴅɪᴀ Tᴏ Gᴇᴛ Tʜᴇ Lɪɴᴋ
➪ /batch › Tᴏ Cʀᴇᴀᴛᴇ Lɪɴᴋ Fᴏʀ Mᴜʟᴛɪᴘʟᴇ Mᴇᴅɪᴀ"""
    FILTER_TXT = "Sᴇʟᴇᴄᴛ Wʜɪᴄʜ Oɴᴇ Yᴏᴜ Wᴀɴᴛ...✨"
    MANUELFILTER_TXT = """<b>Hᴇʟᴘ Fᴏʀ Fɪʟᴛᴇʀs</b>

<i>Fɪʟᴛᴇʀ Is Tʜᴇ Fᴇᴀᴛᴜʀᴇ Wʜᴇʀᴇ Usᴇʀs Cᴀɴ Sᴇᴛ Aᴜᴛᴏᴍᴀᴛᴇᴅ Rᴇᴘʟɪᴇs Fᴏʀ A Pᴀʀᴛɪᴄᴜʟᴀʀ Kᴇʏᴡᴏʀᴅ.</i>

<b>Nᴏᴛᴇ:</b>
1. Tʜɪs Bᴏᴛ Sʜᴏᴜʟᴅ Hᴀᴠᴇ Aᴅᴍɪɴ Pʀɪᴠɪʟᴇɢᴇs.
2. Oɴʟʏ Aᴅᴍɪɴs Cᴀɴ Aᴅᴅ Fɪʟᴛᴇʀs Iɴ A Cʜᴀᴛ.

<b>Cᴏᴍᴍᴀɴᴅs Aɴᴅ Usᴀɢᴇ:</b>
• /filter - Aᴅᴅ A Fɪʟᴛᴇʀ Iɴ Cʜᴀᴛ
• /filters - Lɪsᴛ Aʟʟ Tʜᴇ Fɪʟᴛᴇʀs Oғ A Cʜᴀᴛ
• /del - Dᴇʟᴇᴛᴇ A Sᴘᴇᴄɪғɪᴄ Fɪʟᴛᴇʀ Iɴ Cʜᴀᴛ
• /delall - Dᴇʟᴇᴛᴇ Aʟʟ Fɪʟᴛᴇʀs Iɴ A Cʜᴀᴛ (Oᴡɴᴇʀ Oɴʟʏ)"""
    BUTTON_TXT = """<b>Hᴇʟᴘ Fᴏʀ Bᴜᴛᴛᴏɴs</b>

<i>Tʜɪs Bᴏᴛ Sᴜᴘᴘᴏʀᴛs Bᴏᴛʜ Uʀʟ Aɴᴅ Aʟᴇʀᴛ Iɴʟɪɴᴇ Bᴜᴛᴛᴏɴs.</i>

<b>Nᴏᴛᴇ:</b>
1. Tᴇʟᴇɢʀᴀᴍ Wɪʟʟ Nᴏᴛ Aʟʟᴏᴡ Yᴏᴜ Tᴏ Sᴇɴᴅ Bᴜᴛᴛᴏɴs Wɪᴛʜᴏᴜᴛ Cᴏɴᴛᴇɴᴛ, Sᴏ Cᴏɴᴛᴇɴᴛ Is Mᴀɴᴅᴀᴛᴏʀʏ.
2. Bᴜᴛᴛᴏɴs Sʜᴏᴜʟᴅ Bᴇ Pʀᴏᴘᴇʀʟʏ Pᴀʀsᴇᴅ As Mᴀʀᴋᴅᴏᴡɴ Fᴏʀᴍᴀᴛ."""
    AUTOFILTER_TXT = """<b>Hᴇʟᴘ Fᴏʀ AᴜᴛᴏFɪʟᴛᴇʀ</b>

<i>Aᴜᴛᴏ Fɪʟᴛᴇʀ Is Tʜᴇ Fᴇᴀᴛᴜʀᴇ Tᴏ Fɪʟᴛᴇʀ & Sᴀᴠᴇ Fɪʟᴇs Aᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ Fʀᴏᴍ Cʜᴀɴɴᴇʟ Tᴏ Gʀᴏᴜᴘ.</i>

• /autofilter on - Enable autofilter.
• /autofilter off - Disable autofilter."""
    CONNECTION_TXT = """<b>Hᴇʟᴘ Fᴏʀ Cᴏɴɴᴇᴄᴛɪᴏɴs</b>

<i>Usᴇᴅ Tᴏ Cᴏɴɴᴇᴄᴛ Tʜᴇ Bᴏᴛ Tᴏ PM Fᴏʀ Mᴀɴᴀɢɪɴɢ Fɪʟᴛᴇʀs.</i>

<b>Cᴏᴍᴍᴀɴᴅs Aɴᴅ Usᴀɢᴇ:</b>
• /connect - Cᴏɴɴᴇᴄᴛ A Cʜᴀᴛ Tᴏ Yᴏᴜʀ PM
• /disconnect - Dɪsᴄᴏɴɴᴇᴄᴛ Fʀᴏᴍ A Cʜᴀᴛ
• /connections - Lɪsᴛ Aʟʟ Yᴏᴜʀ Cᴏɴɴᴇᴄᴛɪᴏɴs"""
    ADMIN_TXT = """<b>Hᴇʟᴩ Fᴏʀ Aᴅᴍɪɴꜱ</b>

<i>Tʜɪs Mᴏᴅᴜʟᴇ Oɴʟʏ Wᴏʀᴋs Fᴏʀ Aᴅᴍɪɴs.</i>

<b>Cᴏᴍᴍᴀɴᴅ & Uꜱᴀɢᴇ</b>
• /logs - Gᴇᴛ Rᴇᴄᴇɴᴛ Eʀʀᴏʀꜱ
• /delete - Dᴇʟᴇᴛᴇ A Fɪʟᴇ Fʀᴏᴍ DB
• /users - Gᴇᴛ Lɪꜱᴛ Oꜰ Uꜱᴇʀꜱ
• /chats - Gᴇᴛ Lɪꜱᴛ Oꜰ Cʜᴀᴛꜱ
• /broadcast - Bʀᴏᴀᴅᴄᴀꜱᴛ A Mᴇꜱꜱᴀɢᴇ Tᴏ Aʟʟ Uꜱᴇʀꜱ
• /leave - Lᴇᴀᴠᴇ Fʀᴏᴍ A Cʜᴀᴛ
• /disable - Dɪꜱᴀʙʟᴇ A Cʜᴀᴛ
• /ban_user - Bᴀɴ A Uꜱᴇʀ
• /unban_user - Uɴʙᴀɴ A Uꜱᴇʀ
• /restart - Rᴇsᴛᴀʀᴛ Tʜᴇ Bᴏᴛ"""
    STATUS_TXT = """<b>◉ ᴛᴏᴛᴀʟ ꜰɪʟᴇꜱ: <code>{}</code>
◉ ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ: <code>{}</code>
◉ ᴛᴏᴛᴀʟ ᴄʜᴀṭꜱ: <code>{}</code>
◉ ᴜꜱᴇᴅ ᴅʙ ꜱɪᴢᴇ: <code>{}</code>
◉ ꜰʀᴇᴇ ᴅʙ ꜱɪᴢᴇ: <code>{}</code></b>"""
    LOG_TEXT_G = """<b>#ɴᴇᴡ_ɢʀᴏᴜᴩ

◉ ɢʀᴏᴜᴩ: {a}
◉ ɢ-ɪᴅ: <code>{b}</code>
◉ ʟɪɴᴋ: @{c}
◉ ᴍᴇᴍʙᴇʀꜱ: <code>{d}</code>
◉ ᴀᴅᴅᴇᴅ ʙʏ: {e}

◉ ʙʏ: @{f}</b>"""
    LOG_TEXT_P = """#ɴᴇᴡ_ᴜꜱᴇʀ

◉ ᴜꜱᴇʀ-ɪᴅ: <code>{}</code>
◉ ᴀᴄᴄ-ɴᴀᴍᴇ: {}
◉ ᴜꜱᴇʀɴᴀᴍᴇ: @{}

◉ ʙʏ: @{}</b>"""
    EXTRAMOD_TXT = """<b>Hᴇʟᴩ Fᴏʀ Exᴛʀᴀ Mᴏᴅᴜʟᴇs</b>

<i>Jᴜꜱᴛ Sᴇɴᴅ Aɴʏ Iᴍᴀɢᴇ Tᴏ Eᴅɪᴛ Iᴍᴀɢᴇ.</i>

<b>Cᴏᴍᴍᴀɴᴅꜱ & Uꜱᴀɢᴇ:</b>
• /id - Gᴇᴛ Iᴅ Oғ A Usᴇʀ
• /info - Gᴇᴛ Iɴғᴏʀᴍᴀᴛɪᴏɴ Aʙᴏᴜᴛ A Usᴇʀ
• /imdb - Gᴇᴛ Fɪʟᴍ Iɴғᴏʀᴍᴀᴛɪᴏɴ
• /tts - Cᴏɴᴠᴇʀᴛ Tᴇxᴛ Tᴏ Sᴘᴇᴇᴄʜ
• /json - Gᴇᴛ Mᴇꜱꜱᴀɢᴇ Iɴꜰᴏ
• /telegraph - Uᴘʟᴏᴀᴅ Iᴍᴀɢᴇ Oʀ Vɪᴅᴇᴏ Tᴏ Tᴇʟᴇɢʀᴀᴘʜ"""
    CREATOR_REQUIRED = "❗<b>Yᴏᴜ Hᴀᴠᴇ Tᴏ Bᴇ Tʜᴇ Gʀᴏᴜᴩ Cʀᴇᴀᴛᴏʀ Tᴏ Dᴏ Tʜᴀᴛ.</b>"
    INPUT_REQUIRED = "❗ **Aʀɢᴜᴍᴇɴᴛ Rᴇǫᴜɪʀᴇᴅ.**"
    KICKED = "✔️ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ Kɪᴄᴋᴇᴅ {} Mᴇᴍʙᴇʀꜱ."
    START_KICK = "Rᴇᴍᴏᴠɪɴɢ Iɴᴀᴄᴛɪᴠᴇ Mᴇᴍʙᴇʀs..."
    ADMIN_REQUIRED = "❗<b>I'ᴍ Nᴏᴛ Aɴ Aᴅᴍɪɴ Hᴇʀᴇ.</b>"
    DKICK = "✔️ Kɪᴄᴋᴇᴅ {} Dᴇʟᴇᴛᴇᴅ Aᴄᴄᴏᴜɴᴛꜱ."
    FETCHING_INFO = "<b>Wᴀɪᴛ, I'ᴍ Gᴇᴛᴛɪɴɢ Tʜᴇ Iɴꜰᴏ...</b>"
    SERVER_STATS = """Sᴇʀᴠᴇʀ Sᴛᴀᴛꜱ:

Uᴩᴛɪᴍᴇ: {}
CPU Uꜱᴀɢᴇ: {}%
RAM Uꜱᴀɢᴇ: {}%
Tᴏᴛᴀʟ Dɪꜱᴋ: {}
Uꜱᴇᴅ Dɪꜱᴋ: {} ({}%)
Fʀᴇᴇ Dɪꜱᴋ: {}"""
    BUTTON_LOCK_TEXT = "Hᴇʏ {}, Tʜɪꜱ Iꜱ Nᴏᴛ Fᴏʀ Yᴏᴜ."
    FORCE_SUB_TEXT = "Sᴏʀʀʏ, Yᴏᴜ Hᴀᴠᴇ Tᴏ Jᴏɪɴ Mʏ Cʜᴀɴɴᴇʟ Tᴏ Usᴇ Mᴇ."
    WELCOM_TEXT = "Hᴇʏ {} 👋, Wᴇʟᴄᴏᴍᴇ Tᴏ {}."
    IMDB_TEMPLATE = """<b>Qᴜᴇʀʏ: {query}</b>

🏷 Tɪᴛʟᴇ: <a href={url}>{title}</a>
🎭 Gᴇɴʀᴇꜱ: {genres}
📆 Yᴇᴀʀ: <a href={url}/releaseinfo>{year}</a>
🌟 Rᴀᴛɪɴɢ: <a href={url}/ratings>{rating}</a>/10"""
