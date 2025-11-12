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

class Utilidades(commands.Cog, name="Utilidades"):
    """Comandos úteis e informativos"""

    def __init__(self, bot):
        self.bot = bot
        print(f"✅ Cog Utilidades inicializado com os comandos: {[c.name for c in self.get_commands()]}")

    @commands.command(help="Traduz texto automaticamente para português", aliases=["translate", "tr"])
    async def traduzir(self, ctx, *, texto):
        try:
            t = GoogleTranslator(source='auto', target='pt').translate(texto)
            embed = default.DefaultEmbed.create(
            title="📖 Tradução",
            description=f"**Original:** {texto}\n**Traduzido:** {t}"
            )
        except Exception:
            embed = error.ErrorEmbed.create(
                title="❌ Erro na Tradução",
                description="Ocorreu um erro ao tentar traduzir o texto"
            )

        await ctx.send(embed=embed)

    @commands.command(help="Te dá um conselho", aliases=["advice", "tip"])
    async def conselho(self, ctx, *, translated: bool = True):
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.adviceslip.com/advice")
            data = response.json()
            advice = data['slip']['advice']
        
        if translated:
            advice = GoogleTranslator(source='auto', target='pt').translate(advice)
            embed = default.DefaultEmbed.create(
                title="💡 Conselho",
                description=advice
            )
        else:
            embed = default.DefaultEmbed.create(
                title="💡 Advice",
                description=advice
            )
        await ctx.send(embed=embed)

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

    @commands.group(help="Mostra informações interessantes", aliases=["show", "display"])
    async def ver(self, ctx):
        """Comando para ver coisas interessantes"""
        if ctx.invoked_subcommand is None:
            await ctx.send("❓ Por favor, especifique o que você quer ver. Use `!help ver` para mais informações.")

    @ver.command(name="capital", help="Mostra a capital de um país")
    async def cap(self, ctx, *, pais: str):
        """Mostra a capital de um país"""
        with open('json/capitais.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pais = pais.strip()
        info = data.get(pais.capitalize())
        

        if info:
            capital = info['capital']
            
            embed = default.DefaultEmbed.create(
                title=f"🌍 Capital de {pais.capitalize()}",
                description=f"A capital de **{pais.capitalize()}** é **{capital}**."
            )
            
            await ctx.send(embed=embed)
        else:
            embed = error.ErrorEmbed.create(
                title="❌ País não encontrado!",
                description="Verifique se escreveu corretamente."
            )
            await ctx.send(embed=embed)

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

    @commands.command(name="rps", help="Jogo Pedra, Papel ou Tesoura", aliases=["paperrock", "papelpedra", "rockpaperscissors"])
    async def rps(self, ctx, escolha: str, amount: int):
        from database import get_currency, update_currency
        escolhas_validas = ["pedra", "papel", "tesoura"]
        escolha = escolha.lower()
        if escolha not in escolhas_validas:
            return await ctx.send(embed=error.ErrorEmbed.create(title="❌ Erro", description="Escolha inválida! Use 'pedra', 'papel' ou 'tesoura'."))

        saldo_atual = await get_currency(ctx.author)
        if amount <= 0:
            return await ctx.send(embed=error.ErrorEmbed.create(title="❌ Erro", description="A quantia deve ser maior que zero."))
        if saldo_atual < amount:
            return await ctx.send(embed=error.ErrorEmbed.create(title="❌ Erro", description="Saldo insuficiente para essa aposta."))
        
        bot_escolha = random.choice(escolhas_validas)
        b_emoji = {"pedra": "🪨", "papel": "📄", "tesoura": "✂️"}
        if escolha == bot_escolha:
            embed = default.DefaultEmbed.create(
                title="🤝 Empate!",
                description=f"{escolha} x {bot_escolha}\nNinguém ganha ou perde moedas."
            )
        elif (escolha == "pedra" and bot_escolha == "tesoura") or \
             (escolha == "papel" and bot_escolha == "pedra") or \
             (escolha == "tesoura" and bot_escolha == "papel"):
            embed = success.SuccessEmbed.create(
                title="🏆 Você Ganhou!",
                description=f"{b_emoji[escolha]} x {b_emoji[bot_escolha]}\nParabéns! Você ganhou {amount} moedas."
            )
            await update_currency(ctx.author, amount)
        else:
            await update_currency(ctx.author, -amount)
            embed = error.ErrorEmbed.create(
                title="😞 Você Perdeu!",
                description=f"{escolha} x {bot_escolha}\nVocê perdeu {amount} moedas. Tente novamente!"
            )
        await ctx.send(embed=embed)

async def setup(bot):
    print(f"⚙️ Configurando cog Utilidades...")
    cog = Utilidades(bot)
    await bot.add_cog(cog)
    print(f"✅ Cog Utilidades adicionado com sucesso!")