import discord
import os
import asyncio
from custom.CustomHelp import CustomHelp
from database import is_user_banned
from handlers.global_errors import setup_global_error_handler
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
token = os.getenv("TOKEN")

# Lista de cogs para carregar
COGS = [
    'cogs.prefix.economy',
    'cogs.slash.economy',
    'cogs.prefix.fun',
    'cogs.prefix.games',
    'cogs.prefix.geral',
    'cogs.slash.geral',
    'cogs.prefix.moderation',
    'cogs.prefix.modlog',
    'cogs.prefix.music',
    'cogs.prefix.owner',
    'cogs.prefix.utilidades',
    'cogs.slash.utilidades',
    'cogs.prefix.voiceTTS'
]

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.reactions = True  
intents.messages = True
intents.bans = True
intents.guild_messages = True

help_cmd = CustomHelp()
help_cmd.aliases = ['ajuda']

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=help_cmd # CustomHelp
)

# ------------------------------------------------
# Evento bot pronto
# ------------------------------------------------


@bot.check
async def global_ban_check(ctx):
    if ctx.guild is None:
        return True
    
    if await is_user_banned(ctx.author):
        await ctx.send("⛔ Você está banido de usar o bot.")
        return False

    return True

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="Explorando o Universo"
        )
    )

    # Registra alias do help
    if "ajuda" not in [cmd.name for cmd in bot.commands]:
        bot.all_commands["ajuda"] = bot.all_commands["help"]

    print(f"🤖 Bot conectado como {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comando(s) slash sincronizados")
    except Exception as e:
        print(f"❌ Erro ao sincronizar slash commands: {e}")

    # Sincroniza slash commands
# ------------------------------------------------
# Slash command: /ping
# ------------------------------------------------
@bot.tree.command(name="ping", description="Responde com Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

# ------------------------------------------------
# Inicia o bot
# ------------------------------------------------
async def main():
    print("\n🔄 Iniciando carregamento dos cogs...")
    for cog in COGS:
        try:
            print(f"⚙️ Carregando {cog}...")
            await bot.load_extension(cog)
            print(f"✅ Cog {cog} carregado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar {cog}: {e}")

            
    await setup_global_error_handler(bot)
    await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
