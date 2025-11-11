import pymongo
import os
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = pymongo.MongoClient(mongo_uri)

db = client['economy']
usuarios = db['usuarios']

async def new_user(usuario):
    filter = {"discord_id": usuario.id}
    if usuarios.count_documents(filter) == 0:
        object = {
            "discord_id": usuario.id,
            "nome": usuario.name,
            "saldo": 100,
        }
        usuarios.insert_one(object)
        return object
    else:
        return False
    
async def get_currency(usuario):
    await new_user(usuario)

    filter = {"discord_id": usuario.id}
    user_data = usuarios.find_one(filter)

    return user_data['saldo']

async def update_currency(usuario, amount):
    await new_user(usuario)

    currency = await get_currency(usuario)

    filter = {"discord_id": usuario.id}
    relation = {"$set": {"saldo": currency + amount}}

    usuarios.update_one(filter, relation)