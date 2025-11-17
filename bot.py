import discord
import os
from custom.CustomHelp import CustomHelp
from handlers.global_errors import setup_global_error_handler
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
token = os.getenv("TOKEN")

# Lista de cogs para carregar
COGS = [
    'cogs.geral',
    'cogs.games',
    'cogs.fun',
    'cogs.utilidades',
    'cogs.economy',
    'cogs.moderation',
    'cogs.modlog',
    'cogs.owner'
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
@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="Explorando o Universo"
        )
    )

    await setup_global_error_handler(bot)

    if "ajuda" not in [cmd.name for cmd in bot.commands]:
        bot.all_commands["ajuda"] = bot.all_commands["help"]

    # Carrega os cogs
    print("\n🔄 Iniciando carregamento dos cogs...")
    for cog in COGS:
        try:
            print(f"\n⚙️ Carregando {cog}...")
            await bot.load_extension(cog)
            print(f"✅ Cog {cog} carregado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar {cog}: {e}")
            import traceback
            print(f"Detalhes do erro:\n{traceback.format_exc()}")

    print("\n📋 Lista de todos os comandos registrados:")
    for command in bot.commands:
        print(f"- {command.name}")

    # Sincroniza os slash commands
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
# Inicia o bot
# ------------------------------------------------
bot.run(token)
