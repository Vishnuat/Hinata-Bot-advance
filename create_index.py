import asyncio
from pymongo import TEXT
from motor.motor_asyncio import AsyncIOMotorClient
# Make sure to have an info.py file with your database credentials
from info import FILE_DB_URL, FILE_DB_NAME, COLLECTION_NAME

async def create_text_index():
    """This script will create a text index on the file_name field."""
    print("Connecting to the database...")
    client = AsyncIOMotorClient(FILE_DB_URL)
    db = client[FILE_DB_NAME]
    collection = db[COLLECTION_NAME]

    print(f"Creating text index on '{COLLECTION_NAME}' collection...")
    try:
        # This is the command that creates the index
        await collection.create_index([("file_name", TEXT)])
        print("Text index created successfully! You can now delete this file.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.close()
        print("Database connection closed.")

if __name__ == "__main__":
    asyncio.run(create_text_index())
