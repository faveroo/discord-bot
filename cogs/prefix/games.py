import json
import random
import asyncio
import discord
from helpers.normalize import normalize
from embed import error, success, default
from deep_translator import GoogleTranslator
from discord.ext import commands

class Games(commands.Cog, name="Jogos"):
    """Jogos divertidos para ganhar moedas"""

    def __init__(self, bot):
        self.bot = bot
        self.active_quiz = False
        self.games = {}
        print(f"✅ Cog Games inicializado")
    
    @commands.command(help="Jogo de adivinhar a capital", aliases=["capitals"])
    async def capital(self, ctx):
        if self.active_quiz:
            await ctx.send(embed=error("⚠️ Já existe um quiz ativo. Aguarde terminar!"))
            return
        self.active_quiz = True
        
        with open('json/capitais.json', 'r', encoding='utf-8') as f:
            capitals = json.load(f)

        country = random.choice(list(capitals.keys()))
        capital = capitals[country]['capital']
        
        await ctx.send(f"🌍 **Quiz de Capitais!**\nQual é a capital de **{country}**?\n⏱️ Você(s) têm **30 segundos**!")

        def check(msg):
            return msg.channel == ctx.channel

        try:
            while True:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=30.0,
                    check=check
                )
                if normalize(msg.content) == normalize(capital):
                    from database import update_currency 
                    await update_currency(msg.author, 50)
                    await ctx.send(f"🎉 Parabéns {msg.author.mention}! **{capital}** está correto! +50 Moedas")
                    break
                    
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Tempo esgotado! A capital de **{country}** é **{capital}**.")
        finally:
            self.active_quiz = False

async def setup(bot):
    print(f"⚙️ Configurando cog Games...")
    await bot.add_cog(Games(bot))
    print(f"✅ Cog Games adicionado com sucesso!")