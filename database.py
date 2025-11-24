from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(
    mongo_uri,
    tls=True,
    tlsAllowInvalidCertificates=False,
    tz_aware=True
)


db = client["economy"]
usuarios = db["usuarios"]
modlog = db["modlog"]
auditlog = db["auditlog"]
reminders = db["reminders"]

# ECONOMIA 

async def new_user(usuario):
    filter = {"discord_id": usuario.id}

    existing = await usuarios.count_documents(filter=filter)

    if existing == 0:
        data = {
            "discord_id": usuario.id,
            "nome": usuario.name,
            "saldo": 100,
        }
        await usuarios.insert_one(data)
        return data
    
    return False


async def get_currency(usuario):
    await new_user(usuario)
    filter = {"discord_id": usuario.id}
    user_data = await usuarios.find_one(filter)

    return user_data.get("saldo", 0)


async def update_currency(usuario, amount):
    await new_user(usuario)

    filter = {"discord_id": usuario.id}
    update = {"$inc": {"saldo": amount}}  # mais eficiente

    await usuarios.update_one(filter, update)


async def set_currency(usuario, amount):
    await new_user(usuario)

    filter = {"discord_id": usuario.id}
    update = {"$set": {"saldo": amount}}

    await usuarios.update_one(filter, update)
    return amount


async def get_top_users(limit=10):
    cursor = usuarios.find().sort("saldo", -1).limit(limit)
    return [user async for user in cursor]


async def get_last_daily(usuario):
    await new_user(usuario)
    filter = {"discord_id": usuario.id}
    user_data = await usuarios.find_one(filter)
    return user_data.get("last_daily")


async def set_last_daily(usuario, timestamp):
    await new_user(usuario)
    filter = {"discord_id": usuario.id}
    update = {"$set": {"last_daily": timestamp}}
    await usuarios.update_one(filter, update)


# MODLOG

async def set_modlog(guild_id: int, channel_id: int):
    await modlog.update_one(
        {"guild_id": guild_id},
        {"$set": {"channel_id": channel_id}},
        upsert=True
    )


async def get_modlog(guild_id: int):
    data = await modlog.find_one({"guild_id": guild_id})
    return data["channel_id"] if data else None


# AUDITLOG

async def set_auditlog(guild_id: int, channel_id: int):
    await auditlog.update_one(
        {"guild_id": guild_id},
        {"$set": {"channel_id": channel_id}},
        upsert=True
    )


async def get_auditlog(guild_id: int):
    data = await auditlog.find_one({"guild_id": guild_id})
    return data["channel_id"] if data else None


#   OWNER 

async def reset_economia(valor=150):
    resultado = await usuarios.update_many({}, {"$set": {"saldo": valor}})
    return resultado.modified_count

async def set_banned_user(usuario):
    await new_user(usuario)

    filter = {"discord_id": usuario.id}
    update = {"$set": {"ban": True}}
    await usuarios.update_one(filter, update)

async def remove_banned_user(usuario):
    filter = {"discord_id": usuario.id}
    update = {"$set": {"ban": False}}
    await usuarios.update_one(filter, update)

async def is_user_banned(usuario):
    data = await usuarios.find_one({"discord_id": usuario.id})
    return data and data.get("ban", False)

async def get_banned_users():
    banned = usuarios.find({"ban": True})
    return banned

# UTILIDADES 
async def set_localizacao(usuario, cidade: str):
    await new_user(usuario)
    
    cidade = cidade.strip().title()
    await usuarios.update_one(
        {"discord_id": usuario.id},
        {"$set": {"cidade": cidade}},
        upsert=True
    )

async def get_localizacao(usuario):
    data = await usuarios.find_one({"discord_id": usuario.id})
    if data and "cidade" in data:
        return data["cidade"]
    return None

async def remove_localizacao(usuario):
    filter = {"discord_id": usuario.id}

    update = {"$unset": {"cidade": ""}}

    result = await usuarios.update_one(filter, update)

    return result.modified_count > 0

# REMINDERS

async def create_reminder(user_id: int, message: str, remind_at: datetime, channel_id: int):
    doc = {
        "user_id": user_id,
        "message": message,
        "remind_at": remind_at,
        "created_at": datetime.now(timezone.utc),
        "channel_id": channel_id
    }
    result = await reminders.insert_one(doc)
    return result.inserted_id

async def get_user_reminders(user_id: int):
    cursor = reminders.find({"user_id": user_id}).sort("remind_at", 1)
    return [r async for r in cursor]

async def find_reminder_by_prefix(user_id: int, prefix: str):
    cursor = reminders.find({"user_id": user_id})
    async for doc in cursor:
        if str(doc["_id"]).startswith(prefix):
            return doc
    return None

async def edit_reminder_message(reminder_id: ObjectId, new_message: str):
    await reminders.update_one(
        {"_id": reminder_id},
        {"$set": {"message": new_message}}
    )

async def delete_reminder(reminder_id: ObjectId):
    await reminders.delete_one({"_id": reminder_id})


async def get_pending_reminders():
    now = datetime.now(timezone.utc)
    cursor = reminders.find({"remind_at": {"$gt": now}})
    return [r async for r in cursor]