class script(object):
    START_TXT = """<b>👋 Hello {user},

I'm an advanced filter bot with a lot of features.

Add me to your group and I'll help you manage it! 🚀</b>"""

    HELP_TXT = """<b>Here are the available commands:</b>

- `/start`: Check if I'm alive.
- `/help`: Get this help message.
- `/about`: Learn more about me.
- `/connect`: Connect your group to PM.
- `/disconnect`: Disconnect from a group.
- `/connections`: View your connections.

**Filters:**
- `/filter`: Add a filter.
- `/filters`: View all filters.
- `/del`: Delete a filter.
- `/delall`: Delete all filters.

**Admin:**
- `/stats`: Get bot statistics.
- `/users`: List all users.
- `/chats`: List all chats.
- `/broadcast`: Broadcast a message.
"""

    ABOUT_TXT = """<b>✨ About Me ✨</b>

- **Name:** {bot}
- **Developer:** [VC Movies](https://t.me/VC_Movie)
- **Language:** Python 3
- **Framework:** Pyrogram
- **Database:** MongoDB
- **Version:** 4.6
"""

    SOURCE_TXT = """<b>✨ Source Code ✨</b>

You can find the source code for this bot on GitHub.

- **Repository:** [Hinata-Bot](https://t.me/VC_Movie)
- **Developer:** [VC Movies](https://t.me/VC_Movie)
"""

    FILE_TXT = """<b>➤ Help For File Store</b>

<i>By using this module, you can store files in my database and I will give you a permanent link to access the saved files.</i>

<b>⪼ Commands & Usage</b>
➪ `/link`: Reply to any media to get the link.
➪ `/batch`: Create a link for multiple media.
"""

    FILTER_TXT = "Select which one you want...✨"

    MANUELFILTER_TXT = """<b>Help For Filters</b>

<i>Filters are a feature where users can set automated replies for a particular keyword.</i>

<b>Note:</b>
1. The bot should have admin privileges.
2. Only admins can add filters in a chat.

<b>Commands & Usage:</b>
- `/filter`: Add a filter in a chat.
- `/filters`: List all the filters of a chat.
- `/del`: Delete a specific filter in a chat.
- `/delall`: Delete all filters in a chat (Owner Only).
"""

    BUTTON_TXT = """<b>Help For Buttons</b>

<i>This bot supports both URL and alert inline buttons.</i>

<b>Note:</b>
1. Telegram will not allow you to send buttons without content, so content is mandatory.
2. Buttons should be properly parsed as Markdown format.
"""

    AUTOFILTER_TXT = """<b>Help For AutoFilter</b>

<i>Auto Filter is a feature to filter and save files automatically from a channel to a group.</i>

- `/autofilter on`: Enable autofilter.
- `/autofilter off`: Disable autofilter.
"""

    CONNECTION_TXT = """<b>Help For Connections</b>

<i>Used to connect the bot to PM for managing filters.</i>

<b>Commands & Usage:</b>
- `/connect`: Connect a chat to your PM.
- `/disconnect`: Disconnect from a chat.
- `/connections`: List all your connections.
"""

    ADMIN_TXT = """<b>Help For Admins</b>

<i>This module only works for admins.</i>

<b>Commands & Usage:</b>
- `/logs`: Get recent errors.
- `/delete`: Delete a file from the database.
- `/users`: Get a list of users.
- `/chats`: Get a list of chats.
- `/broadcast`: Broadcast a message to all users.
- `/leave`: Leave a chat.
- `/disable`: Disable a chat.
- `/ban_user`: Ban a user.
- `/unban_user`: Unban a user.
- `/restart`: Restart the bot.
"""

    STATUS_TXT = """<b>◉ Total Files:</b> <code>{}</code>
<b>◉ Total Users:</b> <code>{}</code>
<b>◉ Total Chats:</b> <code>{}</code>
<b>◉ Used DB Size:</b> <code>{}</code>
<b>◉ Free DB Size:</b> <code>{}</code>"""

    LOG_TEXT_G = """<b>#NewGroup</b>

- **Group:** {a}
- **ID:** `{b}`
- **Link:** @{c}
- **Members:** `{d}`
- **Added By:** {e}
- **Bot:** @{f}
"""

    LOG_TEXT_P = """<b>#NewUser</b>

- **ID:** `{}`
- **Name:** {}
- **Username:** @{}
- **Bot:** @{}
"""

    EXTRAMOD_TXT = """<b>Help For Extra Modules</b>

<i>Just send any image to edit it.</i>

<b>Commands & Usage:</b>
- `/id`: Get the ID of a user.
- `/info`: Get information about a user.
- `/imdb`: Get film information.
- `/tts`: Convert text to speech.
- `/json`: Get message info.
- `/telegraph`: Upload an image or video to Telegra.ph.
"""

    CREATOR_REQUIRED = "❗<b>You have to be the group creator to do that.</b>"
    INPUT_REQUIRED = "❗ **Argument required.**"
    KICKED = "✔️ Successfully kicked {} members."
    START_KICK = "Removing inactive members..."
    ADMIN_REQUIRED = "❗<b>I'm not an admin here.</b>"
    DKICK = "✔️ Kicked {} deleted accounts."
    FETCHING_INFO = "<b>Wait, I'm getting the info...</b>"
    SERVER_STATS = """<b>Server Stats:</b>

- **Uptime:** {}
- **CPU Usage:** {}%
- **RAM Usage:** {}%
- **Total Disk:** {}
- **Used Disk:** {} ({}%)
- **Free Disk:** {}"""

    BUTTON_LOCK_TEXT = "Hey {}, this is not for you."
    FORCE_SUB_TEXT = "Sorry, you have to join my channel to use me."
    WELCOM_TEXT = "Hey {} 👋, welcome to {}."
    IMDB_TEMPLATE = """<b>Query: {query}</b>

- **Title:** <a href={url}>{title}</a>
- **Genres:** {genres}
- **Year:** <a href={url}/releaseinfo>{year}</a>
- **Rating:** <a href={url}/ratings>{rating}</a>/10"""
