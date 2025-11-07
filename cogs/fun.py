import json
import random
import httpx
import discord
from discord.ext import commands

class Diversao(commands.Cog, name="Diversão"):
    """Comandos engraçados e curiosos"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Mostra um gato fofo 🐈", aliases=["cat", "kitty", "meow"])
    async def gato(self, ctx):
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.thecatapi.com/v1/images/search")
            data = response.json()
            url = data[0]['url']
            
        embed = discord.Embed(title="Imagem De Gato Aleatório", description="", color=discord.Color.blue())
        embed.add_field(name="Servidor", value=ctx.guild.name, inline=False)
        embed.set_image(url=url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Diversao(bot))
