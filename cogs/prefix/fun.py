import json
import random
import httpx
import discord
from helpers.piadas import piadas
from helpers.piadas2 import piadas2
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
            
        embed = discord.Embed(title="Imagem de Gato", description="", color=discord.Color.blue())
        embed.add_field(name="Servidor", value=ctx.guild.name, inline=False)
        embed.set_image(url=url)
        await ctx.send(embed=embed)
    
    @commands.command(help="Conta uma piada aleatória 🇧🇷", aliases=["joke", "piadas"])
    async def piada(self, ctx):
        piada = random.choice(piadas)
        print(piada)
        await ctx.send(f"😂 {piada}")

    @commands.command(help="piadas v2", aliases=["joke2", "piadas2"])
    async def piada2(self, ctx):
        piada_obj = random.choice(piadas2)
        pergunta = piada_obj['pergunta']
        resposta = piada_obj['resposta']

        await ctx.send(f"😂 {pergunta}\n -{resposta}")

async def setup(bot):
    await bot.add_cog(Diversao(bot))
