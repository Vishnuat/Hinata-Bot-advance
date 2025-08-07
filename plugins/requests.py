import io
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.users_chats_db import db
from info import ADMINS

@Client.on_message(filters.command("requests") & filters.user(ADMINS))
async def view_requests(client, message):
    """
    Shows all the movie requests that were not found.
    """
    await message.reply_chat_action("typing")
    
    if not await db.req.count_documents({}):
        return await message.reply("There are no pending requests.")

    requests = await db.get_all_requests()
    text = "📝 **Pending Movie Requests** 📝\n\n"
    count = 0
    async for request in requests:
        count += 1
        user_info = f"<a href='tg://user?id={request['user_id']}'>User</a>"
        text += f"**{count}.** `{request['query']}`\n   - Requested by: {user_info} in chat `{request['chat_id']}`\n\n"

    if len(text) > 4096:
        file = io.BytesIO(text.encode())
        file.name = "requests.txt"
        await message.reply_document(file, caption="Too many requests to display, sending as a file.")
    else:
        await message.reply(text)

@Client.on_message(filters.command("clearrequests") & filters.user(ADMINS))
async def clear_all_requests(client, message):
    """
    Clears all movie requests from the database.
    """
    buttons = [
        [InlineKeyboardButton("✅ Yes, Clear All", callback_data="confirm_clear_requests")],
        [InlineKeyboardButton("❌ Cancel", callback_data="close_data")]
    ]
    await message.reply(
        "Are you sure you want to delete all pending movie requests? This action cannot be undone.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("confirm_clear_requests"))
async def confirm_clear_requests_cb(client, query):
    if query.from_user.id not in ADMINS:
        return await query.answer("This is an admin-only button.", show_alert=True)
        
    await db.delete_all_requests()
    await query.message.edit("✅ All movie requests have been successfully cleared.")
