import discord
from discord.ext import commands

class Geral(commands.Cog, name="Geral"):
    """Comandos gerais do bot"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Diz olá para o usuário", aliases=["hello", "hi", "hey"])
    async def oi(self, ctx):
        await ctx.send("Olá! 👋 Sou um bot em Python!")

async def setup(bot):
    await bot.add_cog(Geral(bot))
