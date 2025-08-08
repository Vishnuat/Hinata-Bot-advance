import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.users_chats_db import db
from info import ADMINS
from utils import get_ott_releases

@Client.on_message(filters.command("latest"))
async def latest_command(client, message):
    """
    Shows the most searched-for movies in the last 7 days.
    """
    await message.reply_chat_action("typing")
    trending_searches = await db.get_trending_searches(days=7, limit=10)

    if not trending_searches:
        return await message.reply("No trending searches found in the last week.")

    text = "🔥 **Top 10 Trending Searches This Week** 🔥\n\n"
    for i, search in enumerate(trending_searches, 1):
        # Format the search query for display
        query = search['_id'].capitalize()
        text += f"**{i}.** `{query}`\n"

    await message.reply(text)


@Client.on_message(filters.command("ott"))
async def ott_command(client, message):
    """
    Shows upcoming OTT releases and makes the message editable by admins.
    """
    await message.reply_chat_action("typing")
    ott_info = await get_ott_releases()
    header = "📅 **Upcoming OTT Releases** 📅\n\n"
    text = header + ott_info

    buttons = []
    if message.from_user and message.from_user.id in ADMINS:
        buttons.append([InlineKeyboardButton("✍️ Edit This Message", callback_data="edit_ott")])

    sent_message = await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons) if buttons else None)

    # Store the message ID so it can be edited later
    await db.set_ott_message(sent_message.chat.id, sent_message.id)


@Client.on_message(filters.command("set_ott") & filters.user(ADMINS))
async def set_ott_command(client, message):
    """
    Allows admins to manually edit the OTT release message.
    """
    if not message.reply_to_message:
        return await message.reply("Reply to the message you want to set as the new OTT info.")

    ott_message_info = await db.get_ott_message()
    if not ott_message_info:
        return await message.reply("The original OTT message could not be found. Please send `/ott` again first.")

    try:
        header = "📅 **Upcoming OTT Releases** 📅\n\n"
        # Use the text from the replied message
        new_text = header + message.reply_to_message.text.html
        
        # Add the edit button back
        buttons = [
            [InlineKeyboardButton("✍️ Edit This Message", callback_data="edit_ott")]
        ]
        
        await client.edit_message_text(
            chat_id=ott_message_info['chat_id'],
            message_id=ott_message_info['message_id'],
            text=new_text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await message.reply("✅ OTT message has been updated successfully!")
    except Exception as e:
        await message.reply(f"Error updating message: {e}")


@Client.on_callback_query(filters.regex("edit_ott"))
async def edit_ott_callback(client, query):
    """
    Handles the 'Edit This Message' button callback for admins.
    """
    if query.from_user.id not in ADMINS:
        return await query.answer("This is an admin-only button.", show_alert=True)
        
    await query.answer()
    await query.message.reply("To edit this message, reply to the text you want to use with the command `/set_ott`.")
