import json
import random
import asyncio
import httpx
import os
import discord
from embed import error, success, default
from deep_translator import GoogleTranslator
from discord.ext import commands
from dotenv import load_dotenv

class Games(commands.Cog, name="Jogos"):
    """Jogos divertidos para ganhar moedas"""

    def __init__(self, bot):
        self.bot = bot
        print(f"✅ Cog Games inicializado com os comandos: {[c.name for c in self.get_commands()]}")
    
    @commands.command(help="Jogo de adivinhar a capital", aliases=["capitals"])
    async def capital(self, ctx):
        with open('json/capitais.json', 'r', encoding='utf-8') as f:
            capitals = json.load(f)

        country = random.choice(list(capitals.keys()))
        capital = capitals[country]['capital']


        embed = default.DefaultEmbed.create(title="🗺️ Jogo da Capital",)
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

async def setup(bot):
    print(f"⚙️ Configurando cog Games...")
    await bot.add_cog(Games(bot))
    print(f"✅ Cog Games adicionado com sucesso!")