import json
import random
import asyncio
import httpx
import os
import discord
from embed.default import DefaultEmbed
from deep_translator import GoogleTranslator
from discord.ext import commands
from dotenv import load_dotenv

class Utilidades(commands.Cog, name="Utilidades"):
    """Comandos úteis e informativos"""

    def __init__(self, bot):
        self.bot = bot
        print(f"✅ Cog Utilidades inicializado com os comandos: {[c.name for c in self.get_commands()]}")

    @commands.command(help="Traduz texto automaticamente para português", aliases=["translate", "tr"])
    async def traduzir(self, ctx, *, texto):
        t = GoogleTranslator(source='auto', target='pt').translate(texto)
        await ctx.send(f"📘 Tradução: {t}")

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
        with open('json/capitais.json', 'r', encoding='utf-8') as f:
            capitals = json.load(f)

        country = random.choice(list(capitals.keys()))
        capital = capitals[country]['capital']


        embed = DefaultEmbed.create(title="🗺️ Jogo da Capital",)
        embed.add_field(name="País", value=country, inline=False)
        await ctx.send(embed=embed)

        def check(m):
            return m.channel == ctx.channel

        try:
            while True:
                msg = await self.bot.wait_for(
                    "message",
                    check=check,
                    timeout=30.0
                )

                from helpers.normalize import normalize
                if normalize(msg.content.strip()) == "cancelar":
                    await ctx.send("❎ Jogo cancelado.")
                    return

                if normalize(msg.content.strip()) == normalize(capital):
                    embed = discord.Embed(
                        title="✅ Resposta Correta!",
                        description=f"A capital de **{country}** é **{capital}**! +50 moedas.",
                        color=discord.Color.blue()
                    )
                    from database import update_currency
                    await update_currency(ctx.author, 50)
                    await ctx.send(embed=embed)
                    return
                else:
                    await ctx.send("❌ Errado! Tente novamente...")

        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Tempo esgotado! A capital de **{country}** era **{capital}**.")

    @commands.group(help="Mostra informações interessantes", aliases=["show", "display"])
    async def ver(self, ctx):
        """Comando para ver coisas interessantes"""
        if ctx.invoked_subcommand is None:
            await ctx.send("❓ Por favor, especifique o que você quer ver. Use `!help ver` para mais informações.")

    @ver.command(help="Mostra a capital de um país")
    async def cap(self, ctx, *, pais: str):
        """Mostra a capital de um país"""
        with open('json/capitais.json', 'r', encoding='utf-8') as f:
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
        with open('json/capitais.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pais = pais.strip()
        info = data.get(pais.capitalize())

        if info:
            moeda = info['moeda']
            await ctx.send(f"🌍 **{pais.capitalize()}**\n💰 Moeda: {moeda}\n")
        else:
            await ctx.send("❌ País não encontrado! Verifique se escreveu corretamente.")

async def setup(bot):
    print(f"⚙️ Configurando cog Utilidades...")
    cog = Utilidades(bot)
    await bot.add_cog(cog)
    print(f"✅ Cog Utilidades adicionado com sucesso!")