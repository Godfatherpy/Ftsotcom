import motor.motor_asyncio
from config import DB_URI, DB_NAME

# Ensure DB_URI and DB_NAME are defined
if not DB_URI:
    raise ValueError("DB_URI is not set.")
if not DB_NAME:
    raise ValueError("DB_NAME is not set.")

# Initialize the MongoDB client and database
dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database['users']

default_verify = {
    'is_verified': False,
    'verified_time': 0,
    'verify_token': "",
    'link': ""
}

def new_user(id):
    return {
        '_id': id,
        'verify_status': default_verify  # Use default_verify directly
    }

async def present_user(user_id: int):
    found = await user_data.find_one({'_id': user_id})
    return bool(found)

async def add_user(user_id: int):
    user = new_user(user_id)
    try:
        await user_data.insert_one(user)
    except Exception as e:
        print(f"Failed to add user: {e}")

async def db_verify_status(user_id):
    try:
        user = await user_data.find_one({'_id': user_id})
        if user:
            return user.get('verify_status', default_verify)
    except Exception as e:
        print(f"Failed to get verify status: {e}")
    return default_verify

async def db_update_verify_status(user_id, verify):
    try:
        await user_data.update_one({'_id': user_id}, {'$set': {'verify_status': verify}})
    except Exception as e:
        print(f"Failed to update verify status: {e}")

async def full_userbase():
    try:
        user_docs = user_data.find()
        user_ids = [doc['_id'] async for doc in user_docs]
        return user_ids
    except Exception as e:
        print(f"Failed to retrieve full userbase: {e}")
        return []

async def del_user(user_id: int):
    try:
        await user_data.delete_one({'_id': user_id})
    except Exception as e:
        print(f"Failed to delete user: {e}")
