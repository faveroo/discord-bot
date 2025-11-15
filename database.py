import pymongo
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(mongo_uri)

db = client['economy']
usuarios = db['usuarios']
modlog = db['modlog']


# ECONOMIA
async def new_user(usuario):
    filter = {"discord_id": usuario.id}
    existing = await usuarios.count_documents(filter)

    if existing == 0:
        data = {
            "discord_id": usuario.id,
            "nome": usuario.name,
            "saldo": 100,  # saldo inicial
        }
        await usuarios.insert_one(data)
        return data
    
    return False
    
async def get_currency(usuario):
    await new_user(usuario)

    filter = {"discord_id": usuario.id}
    user_data = await usuarios.find_one(filter)

    return user_data['saldo']

async def update_currency(usuario, amount):
    await new_user(usuario)

    currency = await get_currency(usuario)

    filter = {"discord_id": usuario.id}
    relation = {"$set": {"saldo": currency + amount}}

    await usuarios.update_one(filter, relation)

async def set_currency(usuario, amount):
    await new_user(usuario)

    filter = {"discord_id": usuario.id}
    update = {"$set": {"saldo": amount}}

    await usuarios.update_one(filter, update)

    return amount

async def get_top_users(limit=10):
    cursor = usuarios.find().sort("saldo", -1).limit(limit)
    top_users = []
    async for user in cursor:
        top_users.append(user)
    return top_users

async def get_last_daily(usuario):
    await new_user(usuario)
    filter = {"discord_id": usuario.id}
    user_data = await usuarios.find_one(filter)
    return user_data.get("last_daily", None)

async def set_last_daily(usuario, timestamp):
    await new_user(usuario)
    filter = {"discord_id": usuario.id}
    update = {"$set": {"last_daily": timestamp}}
    await usuarios.update_one(filter, update)

async def set_modlog(guild_id: int, channel_id: int):
    """Define ou atualiza o canal de mod-log de um servidor."""
    await modlog.update_one(
        {"guild_id": guild_id},
        {"$set": {"channel_id": channel_id}},
        upsert=True
    )

async def get_modlog(guild_id: int):
    """Retorna o ID do canal configurado ou None."""
    data = await modlog.find_one({"guild_id": guild_id})
    return data["channel_id"] if data else None

async def reset_economia(valor=150):
    """
    Reseta a economia de todos os usuários para 'valor'.
    """
    resultado = await usuarios.update_many(
        {},  # filtro vazio = todos os usuários
        {"$set": {"saldo": valor}}
    )
    return resultado.modified_count