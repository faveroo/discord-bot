import discord
import random
from discord.ext import commands
from discord import app_commands

class GeralSlash(commands.Cog):
    """Comandos gerais do bot"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="number", description="Responde com um número aleatório")
    async def number(self, interaction: discord.Interaction):
        num = random.randint(1, 100)
        await interaction.response.send_message(f"Seu número aleatório é: {num}")
    
async def setup(bot):
    await bot.add_cog(GeralSlash(bot))
