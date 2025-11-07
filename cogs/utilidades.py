import json
import random
import asyncio
import httpx
from deep_translator import GoogleTranslator
from discord.ext import commands

class Utilidades(commands.Cog, name="Utilidades"):
    """Comandos úteis e informativos"""

    def __init__(self, bot):
        self.bot = bot
        print(f"✅ Cog Utilidades inicializado com os comandos: {[c.name for c in self.get_commands()]}")

    @commands.command(help="Conta uma piada aleatória", aliases=["joke", "jokes", "piadas"])
    async def piada(self, ctx):
        async with httpx.AsyncClient() as client:
            response = await client.get("https://official-joke-api.appspot.com/random_joke")
            joke = response.json()
        await ctx.send(f"{joke['setup']} ... {joke['punchline']}")

    @commands.command(help="Te dá um conselho", aliases=["advice", "tip"])
    async def conselho(self, ctx):
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.adviceslip.com/advice")
            data = response.json()
            advice = data['slip']['advice']
            translated_advice = GoogleTranslator(source='auto', target='pt').translate(advice)
        await ctx.send(f"💡 Conselho: {translated_advice}")

    @commands.command(help="Jogo de adivinhar a capital", aliases=["capitals"])
    async def capital(self, ctx):
        with open('json/capitals.json', 'r', encoding='utf-8') as f:
            capitals = json.load(f)

        country = random.choice(list(capitals.keys()))
        capital = capitals[country]['capital']

        await ctx.send(f"Qual é a capital de {country}?")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30.0)
            if msg.content.strip().lower() == capital.lower():
                await ctx.send(f"✅ Correto! A capital de {country} é {capital}!")
            else:
                await ctx.send(f"❌ Errado! A capital de {country} é {capital}.")
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Tempo esgotado! A capital de {country} é {capital}.")

    @commands.group(help="Mostra informações interessantes", aliases=["show", "display"])
    async def ver(self, ctx):
        """Comando para ver coisas interessantes"""
        if ctx.invoked_subcommand is None:
            await ctx.send("❓ Por favor, especifique o que você quer ver. Use `!help ver` para mais informações.")

    @ver.command(help="Mostra a capital de um país")
    async def cap(self, ctx, *, pais: str):
        """Mostra a capital de um país"""
        with open('json/capitals.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pais = pais.strip()
        info = data.get(pais.capitalize())

        if info:
            capital = info['capital']
            await ctx.send(f"🌍 **{pais.capitalize()}**\n📍 Capital: {capital}\n")
        else:
            await ctx.send("❌ País não encontrado! Verifique se escreveu corretamente.")

    @ver.command(help="Mostra a moeda de um país")
    async def moeda(self, ctx, *, pais: str):
        """Mostra a moeda de um país"""
        with open('json/capitals.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pais = pais.strip()
        info = data.get(pais.capitalize())

        if info:
            moeda = info['currency']
            await ctx.send(f"🌍 **{pais.capitalize()}**\n💰 Moeda: {moeda}\n")
        else:
            await ctx.send("❌ País não encontrado! Verifique se escreveu corretamente.")
async def setup(bot):
    print(f"⚙️ Configurando cog Utilidades...")
    cog = Utilidades(bot)
    await bot.add_cog(cog)
    print(f"✅ Cog Utilidades adicionado com sucesso!")