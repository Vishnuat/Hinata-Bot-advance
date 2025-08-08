import motor.motor_asyncio
from datetime import datetime, timedelta
from info import DATABASE_NAME, DATABASE_URL, IMDB, IMDB_TEMPLATE, MELCOW_NEW_USERS, P_TTI_SHOW_OFF, SINGLE_BUTTON, SPELL_CHECK_REPLY, PROTECT_CONTENT, AUTO_POST

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups
        self.queries = self.db.search_queries
        self.ott = self.db.ott_message
        self.req = self.db.requests # New collection for requests

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
        )

    def new_group(self, id, title, username):
        return dict(
            id = id,
            title = title,
            username = username,
            chat_status=dict(
                is_disabled=False,
                reason="",
            ),
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
    
    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})
    
    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'id':int(id)})
        if not user:
            return default
        return user.get('ban_status', default)

    async def get_all_users(self):
        return self.col.find({})
    
    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def delete_chat(self, chat_id):
        await self.grp.delete_many({'id': int(chat_id)})

    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        return b_users, b_chats
    
    async def add_chat(self, chat, title, username):
        chat = self.new_group(chat, title, username)
        await self.grp.insert_one(chat)
    
    async def get_chat(self, chat):
        chat = await self.grp.find_one({'id':int(chat)})
        return False if not chat else chat.get('chat_status')
    
    async def re_enable_chat(self, id):
        chat_status=dict(
            is_disabled=False,
            reason="",
            )
        await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status': chat_status}})
        
    async def update_settings(self, id, settings):
        await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})
        
    async def get_settings(self, id):       
        default = {
            'button': SINGLE_BUTTON,
            'botpm': P_TTI_SHOW_OFF,
            'file_secure': PROTECT_CONTENT,
            'imdb': IMDB,
            'spell_check': SPELL_CHECK_REPLY,
            'welcome': MELCOW_NEW_USERS,
            'template': IMDB_TEMPLATE,
            'auto_post': AUTO_POST
        }
        chat = await self.grp.find_one({'id':int(id)})
        if chat:
            return chat.get('settings', default)
        return default

    async def disable_chat(self, chat, reason="No Reason"):
        chat_status=dict(
            is_disabled=True,
            reason=reason,
            )
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}})
    
    async def total_chat_count(self):
        count = await self.grp.count_documents({})
        return count
    
    async def get_all_chats(self):
        return self.grp.find({})

    async def get_db_size(self):
        return (await self.db.command("dbstats"))['dataSize']

    async def log_search(self, query):
        await self.queries.insert_one({'query': query.lower(), 'timestamp': datetime.utcnow()})

    async def get_trending_searches(self, days=7, limit=10):
        start_date = datetime.utcnow() - timedelta(days=days)
        pipeline = [
            {'$match': {'timestamp': {'$gte': start_date}}},
            {'$group': {'_id': '$query', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': limit}
        ]
        return await self.queries.aggregate(pipeline).to_list(length=limit)

    async def set_ott_message(self, chat_id, message_id):
        await self.ott.update_one({'_id': 'ott_message_info'}, {'$set': {'chat_id': chat_id, 'message_id': message_id}}, upsert=True)

    async def get_ott_message(self):
        return await self.ott.find_one({'_id': 'ott_message_info'})
        
    # New functions for handling movie requests
    async def add_request(self, chat_id, user_id, query):
        """Saves a movie request to the database."""
        request = {
            'chat_id': chat_id,
            'user_id': user_id,
            'query': query,
            'timestamp': datetime.utcnow()
        }
        await self.req.insert_one(request)

    async def get_all_requests(self):
        """Gets all movie requests from the database."""
        return self.req.find({}).sort('timestamp', -1)

    async def delete_all_requests(self):
        """Clears all movie requests from the database."""
        await self.req.delete_many({})

    async def set_index_progress(self, chat_id, last_message_id):
        """Saves the indexing progress for a chat."""
        await self.db.index_progress.update_one(
            {'_id': chat_id},
            {'$set': {'last_id': last_message_id}},
            upsert=True
        )

    async def get_index_progress(self, chat_id):
        """Gets the indexing progress for a chat."""
        progress = await self.db.index_progress.find_one({'_id': chat_id})
        return progress['last_id'] if progress else 0

    async def clear_index_progress(self, chat_id):
        """Clears the indexing progress for a chat."""
        await self.db.index_progress.delete_one({'_id': chat_id})

db = Database(DATABASE_URL, DATABASE_NAME)
