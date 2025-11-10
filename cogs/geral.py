import discord
from discord.ext import commands
from discord import app_commands

class Geral(commands.Cog, name="Geral"):
    """Comandos gerais do bot"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Diz olá para o usuário", aliases=["hello", "hi", "hey"])
    async def oi(self, ctx):
        await ctx.send("Olá! 👋 Sou um bot em Python!")

    @commands.command(help="Marca everyone")
    async def todos(self, ctx):
        await ctx.send("@everyone 👋")

    @app_commands.command(name="number", description="Responde com um número aleatório")
    async def number(self, interaction: discord.Interaction):
        import random
        num = random.randint(1, 100)
        await interaction.response.send_message(f"Seu número aleatório é: {num}")

async def setup(bot):
    await bot.add_cog(Geral(bot))
