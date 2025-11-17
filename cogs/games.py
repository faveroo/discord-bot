import json
import random
import asyncio
import discord
from helpers.normalize import normalize
from embed import error, success, default
from deep_translator import GoogleTranslator
from discord.ext import commands
from dotenv import load_dotenv

class Games(commands.Cog, name="Jogos"):
    """Jogos divertidos para ganhar moedas"""

    def __init__(self, bot):
        self.bot = bot
        self.games = {}
        print(f"✅ Cog Games inicializado")
    
    @commands.command(help="Jogo de adivinhar a capital", aliases=["capitals"])
    async def capital(self, ctx):
        with open('json/capitais.json', 'r', encoding='utf-8') as f:
            capitals = json.load(f)

        country = random.choice(list(capitals.keys()))
        capital = capitals[country]['capital']
        
        self.games[ctx.channel.id] = {
        "country": country,
        "capital": capital.lower(),
        "players": set()
    }


        embed = default.DefaultEmbed.create(
            title="🗺️ Jogo da Capital",
            description=f"Adivinhe a capital do país abaixo:\n\n**{country}**"
            )
        embed.set_footer(text="Digite 'cancelar' para parar o jogo.")
        await ctx.send(embed=embed)

        async def fechar_jogo():
            await asyncio.sleep(30)
            if ctx.channel.id in self.games:
                capital = self.games[ctx.channel.id]["capital"]
                await ctx.send(f"⏰ Tempo esgotado! A capital era **{capital}**.")
                del self.games[ctx.channel.id]

        asyncio.create_task(fechar_jogo())

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        channel_id = message.channel.id
    

        # se não há jogo nesse canal, ignorar
        if channel_id not in self.games:
            return

        game = self.games[channel_id]
        resposta = message.content.lower().strip()

        # cancelar
        if resposta == "cancelar":
            await message.channel.send("❎ O jogo foi cancelado.")
            del self.games[channel_id]
            return

        # resposta correta
        if normalize(resposta) == normalize(game["capital"]):
            country = game["country"]
            capital = game["capital"]

            # evita dar recompensa duplicada
            if message.author.id not in game["players"]:
                from database import update_currency
                await update_currency(message.author, 50)
                game["players"].add(message.author.id)

            await message.channel.send(
                f"🎉 {message.author.mention} acertou! A capital de **{country}** é **{capital}**!"
            )
        else:
            await message.channel.send("Tente novamente")
            # ENCERRA o jogo
        await self.bot.process_commands(message)
        del self.games[channel_id]

async def setup(bot):
    print(f"⚙️ Configurando cog Games...")
    await bot.add_cog(Games(bot))
    print(f"✅ Cog Games adicionado com sucesso!")