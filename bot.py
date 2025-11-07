import discord
import os
import httpx
import json
import random
import asyncio
from deep_translator import GoogleTranslator
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------------------------------------
# Evento bot pronto
# ------------------------------------------------
@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="Explorando o Mainframe"
        )
    )

    # ✅ Sincroniza APENAS os slash commands (temos só 1)
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comando(s) slash sincronizados")
    except Exception as e:
        print(f"❌ Erro ao sincronizar slash commands: {e}")

    print(f"🤖 Bot conectado como {bot.user}")

# ------------------------------------------------
# Slash command: /ping
# ------------------------------------------------
@bot.tree.command(name="ping", description="Responde com Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

# ------------------------------------------------
# Comando !oi
# ------------------------------------------------
@bot.command()
async def oi(ctx):
    await ctx.send("Olá! 👋 Sou um bot em Python!")

# ------------------------------------------------
# Comando !piada
# ------------------------------------------------
@bot.command()
async def piada(ctx):
    async with httpx.AsyncClient() as client:
        response = await client.get("https://official-joke-api.appspot.com/random_joke")
        joke = response.json()
    await ctx.send(f"{joke['setup']} ... {joke['punchline']}")

# ------------------------------------------------
# Comando !traduzir
# ------------------------------------------------
@bot.command()
async def traduzir(ctx, *, texto):
    t = GoogleTranslator(source='auto', target='pt').translate(texto)
    await ctx.send(f"📘 Tradução: {t}")
    
@bot.command()
async def gato(ctx):
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.thecatapi.com/v1/images/search")
        data = response.json()
        url = data['url']
        
    embed = discord.Embed(title="Image De Gato", description="", color=discord.Color.blue())
    
    embed.add_field(name="Nome", value=ctx.guild.name, inline=False)
    embed.set_image(url=url)

    await ctx.send(embed=embed)
# ------------------------------------------------
# Comando !capital
# ------------------------------------------------
@bot.command()
async def capital(ctx):
    with open('json/capitals.json', 'r', encoding='utf-8') as f:
        capitals = json.load(f)

    country = random.choice(list(capitals.keys()))
    capital = capitals[country]

    await ctx.send(f"Qual é a capital de {country}?")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        if msg.content.strip().lower() == capital.lower():
            await ctx.send("✅ Correto! 🎉")
        else:
            await ctx.send(f"❌ Errado! A capital de {country} é `{capital}`.")
    except asyncio.TimeoutError:
        await ctx.send(f"⏳ Tempo esgotado! A capital de {country} é `{capital}`.")

# ------------------------------------------------
# Grupo Ver
# ------------------------------------------------
@bot.group()
async def ver(ctx):
    """Comando para ver coisas interessantes"""
    if ctx.invoked_subcommand is None:
        await ctx.send("Subcomando válidos: capital | moeda")

@ver.command()
async def capital(ctx, *, pais: str):
    """Mostra a capital de um país"""
    with open('json/capitals.json') as f:
        data = json.load(f)
    
    pais = pais.strip()
    capital = data.get(pais)
    
    if capital and capital != "Sem capital":
        await ctx.send(f"🌍 A capital de {pais} é {capital}")
    elif capital == "Sem capital":
        await ctx.send(f"🙁 {pais} não possuí capital")
    else:
        await ctx.send(f"❌ País não encontrado")
# ------------------------------------------------
bot.run(token)
