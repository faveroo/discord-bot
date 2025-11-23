import json
import random
import httpx
import discord
from deep_translator import GoogleTranslator
from embed.default import DefaultEmbed
from helpers.piadas import piadas
from helpers.piadas2 import piadas2
from discord.ext import commands

class Diversao(commands.Cog, name="Diversão"):
    """Comandos engraçados e curiosos"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gato", help="Mostra um gato fofo 🐈", aliases=["cat", "kitty", "meow"])
    async def gato(self, ctx):
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.thecatapi.com/v1/images/search")
            data = response.json()
            url = data[0]['url']
            
        embed = DefaultEmbed.create(title="Imagem de Gato", description="")
        embed.add_field(name="Servidor", value=ctx.guild.name, inline=False)
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @commands.group(name="fatos")
    async def fatos(self, ctx):
        """Comando para ver fatos sobre coisas no geral"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Digite `!help fatos` para saber mais!")

    @fatos.command(name="gato", description="Fatos sobre gatos")
    async def fatos_gato(self, ctx):
        async with httpx.AsyncClient() as client:
            response = await client.get("https://meowfacts.herokuapp.com/")
            data = response.json()
            fact = data['data'][0]
        
        fato = GoogleTranslator(source="auto", target="pt").translate(fact)
        embed = DefaultEmbed.create(
            title="Fatos sobre gatos",
            description=fato
        )
        await ctx.send(embed=embed)

    @fatos.command(name="cachorro", description="Fatos sobre cachorros")
    async def fatos_cachorro(self, ctx):
        async with httpx.AsyncClient() as client:
            response = await client.get("https://dogapi.dog/api/v2/facts?limit=1")
            data = response.json()
            fact = data['data'][0]['attributes']['body']

        fato = GoogleTranslator(source="auto", target="pt").translate(fact)
        embed = DefaultEmbed.create(
            title="Fatos sobre cachorros",
            description=fato
        )
        await ctx.send(embed=embed)

    @commands.command(name="cachorro", help="Mostra um cachorro fofo 🐕", aliases=["dog"])
    async def cachorro(self, ctx):
        async with httpx.AsyncClient() as client:
            response = await client.get("https://dog.ceo/api/breeds/image/random")
            data = response.json()
            url = data['message']
        
        embed = DefaultEmbed.create(title="Imagem de Cachorro", description="")
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
