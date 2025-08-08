import logging
from struct import pack
import re
import base64
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from info import FILE_DB_URL, FILE_DB_NAME, COLLECTION_NAME, MAX_RIST_BTNS

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


client = AsyncIOMotorClient(FILE_DB_URL)
db = client[FILE_DB_NAME]
instance = Instance.from_db(db)

@instance.register
class Media(Document):
    file_id = fields.StrField(attribute='_id')
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)

    class Meta:
        collection_name = COLLECTION_NAME


async def save_file(media):
    """Saves a file to the database."""
    file_id, file_ref = unpack_new_file_id(media.file_id)
    # Sanitize file name for better search results
    file_name = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(media.file_name))
    try:
        file = Media(
            file_id=file_id,
            file_ref=file_ref,
            file_name=file_name,
            file_size=media.file_size,
            file_type=media.file_type,
            mime_type=media.mime_type
        )
    except ValidationError:
        logger.exception('Error Occurred While Saving File In Database')
        return False, 2
    else:
        try:
            await file.commit()
        except DuplicateKeyError:
            logger.warning(f"{getattr(media, 'file_name', 'NO FILE NAME')} is already saved in database")
            return False, 0
        else:
            logger.info(f"{getattr(media, 'file_name', 'NO FILE NAME')} is saved in database")
            return True, 1


async def get_search_results(query, file_type=None, max_results=MAX_RIST_BTNS, offset=0, filter=False):
    """
    Returns search results from the database using a regex for broad compatibility.
    """
    query = query.strip()
    if not query:
        return [], '', 0

    # Use regex for a more forgiving search that doesn't rely on a text index.
    # The 'i' option makes the search case-insensitive.
    filter_query = {'file_name': {'$regex': re.escape(query), '$options': 'i'}}

    if file_type:
        filter_query['file_type'] = file_type

    total_results = await Media.collection.count_documents(filter_query)
    next_offset = offset + max_results
    if next_offset > total_results:
        next_offset = ''

    # Find documents. Sorting by relevance isn't possible with regex, but we can find the files.
    cursor = Media.collection.find(
        filter_query
    ).skip(offset).limit(max_results)

    files = await cursor.to_list(length=max_results)

    # Convert the dictionary results back to Media objects for compatibility
    media_files = [Media.build_from_mongo(file) for file in files]

    return media_files, next_offset, total_results


async def get_file_details(query):
    """Returns the details of a file."""
    filter = {'file_id': query}
    cursor = Media.find(filter)
    filedetails = await cursor.to_list(length=1)
    return filedetails


def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")


def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")


def unpack_new_file_id(new_file_id):
    """Return file_id, file_ref"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref
