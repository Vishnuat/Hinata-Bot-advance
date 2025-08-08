import logging
import re
import asyncio
from urllib.parse import quote_plus
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from info import CHANNELS, ADMINS, UPDATE_CHANNEL
from database.ia_filterdb import Media, unpack_new_file_id
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import temp, detect_language

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()

# A list to hold file documents for bulk writing
file_batch = []
BATCH_SIZE = 200  # Number of files to save in one batch

# --- CHANGE IS HERE ---
# List of keywords to exclude from indexing
EXCLUDE_KEYWORDS = ['dvdrip', 'predvd', 'hqclean', 'camrip', 'pre-hd', 'hdts']
# --- END OF CHANGE ---


async def save_file_batch():
    """Saves a batch of files to the database using a bulk write operation."""
    global file_batch
    if not file_batch:
        return 0, 0

    try:
        # Use insert_many for a high-speed bulk write
        result = await Media.collection.insert_many(file_batch, ordered=False)
        saved_count = len(result.inserted_ids)
        duplicate_count = len(file_batch) - saved_count
        file_batch = []  # Clear the batch after saving
        return saved_count, duplicate_count
    except Exception as e:
        logger.error(f"Error during bulk save: {e}")
        file_batch = []
        return 0, len(file_batch) # Return 0 saved, all as duplicates/errors

@Client.on_message(filters.chat(CHANNELS) & (filters.document | filters.video | filters.audio))
async def media(bot, message):
    """Handles new media messages in specified channels for indexing."""
    media = getattr(message, message.media.value, None)
    if not media:
        return

    # Prepare file document
    file_id, file_ref = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(getattr(media, "file_name", "")))
    
    # --- CHANGE IS HERE ---
    # Check if any of the exclude keywords are in the file name
    if any(keyword in file_name.lower() for keyword in EXCLUDE_KEYWORDS):
        logger.info(f"Skipped file due to excluded keyword: {file_name}")
        return
    # --- END OF CHANGE ---

    file_doc = {
        '_id': file_id,
        'file_ref': file_ref,
        'file_name': file_name,
        'file_size': media.file_size,
        'file_type': message.media.value,
        'mime_type': getattr(media, "mime_type", ""),
        'caption': message.caption.html if message.caption else ""
    }

    file_batch.append(file_doc)

    # New file notification
    if UPDATE_CHANNEL:
        try:
            # Combine file name and caption for language detection
            text_for_lang_detection = file_doc['file_name']
            if file_doc['caption']:
                text_for_lang_detection += " " + file_doc['caption']

            language = detect_language(text_for_lang_detection)
            notification_text = (
                "**New File Added**\n\n"
                f"**File Name:** `{file_doc['file_name']}`\n"
                f"**Language:** `{language}`"
            )

            # Create the search button
            search_query = quote_plus(file_doc['file_name'])
            button_url = f"https://t.me/{temp.U_NAME}?start=search_{search_query}"
            buttons = [[
                InlineKeyboardButton("📥 Download", url=button_url)
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)

            await bot.send_message(
                UPDATE_CHANNEL,
                notification_text,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Failed to send new file notification: {e}")

    # If the batch is full, save it to the database
    if len(file_batch) >= BATCH_SIZE:
        await save_file_batch()

@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("Cancelling Indexing...", show_alert=True)

    _, chat, lst_msg_id = query.data.split("#")
    if lock.locked():
        return await query.answer('Wait until the previous process is complete.', show_alert=True)

    msg = query.message
    button = InlineKeyboardMarkup([[
        InlineKeyboardButton('🚫 Cancel', "index_cancel")
    ]])
    await msg.edit("Indexing has started ✨", reply_markup=button)
    try:
        chat = int(chat)
    except:
        pass
    await index_files_to_db(int(lst_msg_id), chat, msg, bot)

@Client.on_message((filters.forwarded | (filters.regex("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0_9]+)/(\d+)$")) & filters.text) & filters.private & filters.incoming & filters.user(ADMINS))
async def send_for_index(bot, message):
    # Logic to handle index command remains the same
    if message.text:
        regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0_9]+)/(\d+)$")
        match = regex.match(message.text)
        if not match: return await message.reply('Invalid link')
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric(): chat_id  = int(("-100" + chat_id))
    elif message.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    else: return
    try: await bot.get_chat(chat_id)
    except ChannelInvalid: return await message.reply('This may be a private channel/group. Make me an admin to index files.')
    except (UsernameInvalid, UsernameNotModified): return await message.reply('Invalid Link specified.')
    except Exception as e: return await message.reply(f'Error: {e}')
    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except:
        return await message.reply('Make sure I am an admin in the channel if it is private.')
    if k.empty:
        return await message.reply('This may be a group and I am not an admin.')

    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton('✨ Yes', callback_data=f'index#{chat_id}#{last_msg_id}')
    ], [
        InlineKeyboardButton('🚫 Close', callback_data='close_data')
    ]])
    await message.reply(f'Do you want to index this channel/group?\n\nChat ID/Username: `{chat_id}`\nLast Message ID: `{last_msg_id}`', reply_markup=buttons)

@Client.on_message(filters.command('setskip') & filters.user(ADMINS))
async def set_skip_number(bot, message):
    if len(message.command) == 2:
        try:
            skip = int(message.text.split(" ", 1)[1])
            temp.CURRENT = int(skip)
            await message.reply(f"Successfully set skip number as {skip}")
        except:
            await message.reply("Skip number should be an integer.")
    else:
        await message.reply("Give me a skip number.")

async def index_files_to_db(lst_msg_id, chat, msg, bot):
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0
    global file_batch

    async with lock:
        try:
            current = temp.CURRENT
            temp.CANCEL = False
            async for message in bot.iter_messages(chat, lst_msg_id, temp.CURRENT):
                if temp.CANCEL:
                    break
                current += 1
                if current % 100 == 0:
                    # Save the current batch before updating status
                    saved, dup = await save_file_batch()
                    total_files += saved
                    duplicate += dup
                    
                    can = [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
                    reply = InlineKeyboardMarkup(can)
                    try:
                        await msg.edit_text(
                            text=f"Total Messages Fetched: `{current}`\nTotal Files Saved: `{total_files}`\nDuplicate Files Skipped: `{duplicate}`\nDeleted Messages Skipped: `{deleted}`\nNon-Media Skipped: `{no_media}`\nUnsupported Files: `{unsupported}`\nErrors: `{errors}`",
                            reply_markup=reply
                        )
                    except FloodWait as t:
                        await asyncio.sleep(t.value)

                if message.empty:
                    deleted += 1
                    continue
                elif not message.media:
                    no_media += 1
                    continue
                elif message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
                    unsupported += 1
                    continue

                media = getattr(message, message.media.value, None)
                if not media:
                    unsupported += 1
                    continue

                # Prepare file document for batching
                file_id, file_ref = unpack_new_file_id(media.file_id)
                file_name = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(getattr(media, "file_name", "")))
                
                # --- CHANGE IS HERE ---
                # Check if any of the exclude keywords are in the file name
                if any(keyword in file_name.lower() for keyword in EXCLUDE_KEYWORDS):
                    logger.info(f"Skipped file due to excluded keyword: {file_name}")
                    continue
                # --- END OF CHANGE ---

                file_doc = {
                    '_id': file_id,
                    'file_ref': file_ref,
                    'file_name': file_name,
                    'file_size': media.file_size,
                    'file_type': message.media.value,
                    'mime_type': getattr(media, "mime_type", ""),
                    'caption': message.caption.html if message.caption else ""
                }
                file_batch.append(file_doc)

                # If batch size is reached, save the batch
                if len(file_batch) >= BATCH_SIZE:
                    saved, dup = await save_file_batch()
                    total_files += saved
                    duplicate += dup

        except Exception as e:
            logger.exception(e)
            await msg.edit(f'Error: {e}')
        finally:
            # Save any remaining files in the batch
            saved, dup = await save_file_batch()
            total_files += saved
            duplicate += dup
            
            await msg.edit(f'Successfully Saved `{total_files}` files to the database!\n'
                           f'Duplicate Files Skipped: `{duplicate}`\n'
                           f'Deleted Messages Skipped: `{deleted}`\n'
                           f'Non-Media Messages Skipped: `{no_media}`\n'
                           f'Unsupported Files: `{unsupported}`\n'
                           f'Errors Occurred: `{errors}`')
