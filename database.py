from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(mongo_uri, tls=True, tlsAllowInvalidCertificates=False)


db = client["economy"]
usuarios = db["usuarios"]
modlog = db["modlog"]

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


# RESETAR ECONOMIA

async def reset_economia(valor=150):
    resultado = await usuarios.update_many({}, {"$set": {"saldo": valor}})
    return resultado.modified_count

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