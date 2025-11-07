from deep_translator import GoogleTranslator
from discord.ext import commands

class Traducao(commands.Cog, name="Tradução"):
    """Comandos relacionados à tradução"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Traduz texto automaticamente para português", aliases=["translate", "tr"])
    async def traduzir(self, ctx, *, texto):
        t = GoogleTranslator(source='auto', target='pt').translate(texto)
        await ctx.send(f"📘 Tradução: {t}")

async def setup(bot):
    await bot.add_cog(Traducao(bot))