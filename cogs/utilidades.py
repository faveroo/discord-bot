import json
import random
import asyncio
import httpx
import aiohttp
import os
import discord
from bs4 import BeautifulSoup
from embed import error, success, default
from deep_translator import GoogleTranslator
from discord.ext import commands
from urllib.parse import quote
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

    @commands.command(help="Te dá um conselho no idioma desejado. Ex: pt, en, es...", aliases=["advice", "tip"], usage="[idioma]")
    async def conselho(self, ctx, *, translated: str = "pt"):
        lang = (translated or "pt").strip().lower()
        translator = GoogleTranslator()
        supported_langs = translator.get_supported_languages(as_dict=True)
        # print(supported_langs)
        
        if lang not in supported_langs.values():
            lang = "pt"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("https://api.adviceslip.com/advice")
                response.raise_for_status()
                data = response.json()
                advice = data["slip"]["advice"]
            except Exception as e:
                return await ctx.send(f"❌ Erro ao obter conselho: {e}")

        translated_advice = ""
        try:
            translated_advice = GoogleTranslator(source="auto", target=lang).translate(advice)
        except Exception as e:
            print(f"Erro na tradução - {e}")
            translated_advice = advice  # fallback caso dê erro

        title = "💡 Advice" if lang.startswith("en") else "💡 Conselho"

        embed = default.DefaultEmbed.create(
            title=title,
            description=translated_advice
        )

        await ctx.send(embed=embed)

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
        
        pais = pais.strip().title()
        info = data.get(pais)
        

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
        
        pais = pais.strip().title()
        info = data.get(pais)

        if info:
            moeda = info['moeda']
            await ctx.send(f"🌍 **{pais.capitalize()}**\n💰 Moeda: {moeda}\n")
        else:
            await ctx.send("❌ País não encontrado! Verifique se escreveu corretamente.")

    @commands.command(name="rps", help="Jogo Pedra, Papel ou Tesoura", aliases=["paperrock", "papelpedra", "rockpaperscissors"])
    async def rps(self, ctx, escolha: str, amount: int = 0):
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
                description=f"{b_emoji[escolha]} x {b_emoji[bot_escolha]}\nNinguém ganha ou perde moedas."
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
                description=f"{b_emoji[escolha]} x {b_emoji[bot_escolha]}\nVocê perdeu {amount} moedas. Tente novamente!"
            )
        await ctx.send(embed=embed)
    
    @commands.command(name="avatar", help="Exibe o avatar do usuário", aliases=["icon", "pfp"])
    async def avatar(self, ctx, user: discord.User = None):
        if not user:
            user = ctx.author
        
        avatar_url = user.avatar.url if user.avatar else user.default_avatar.url

        embed = default.DefaultEmbed.create(
            title=f"Avatar de {user}"
        )
        embed.set_image(url=avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="banner", help="Exibe o banner do usuário", aliases=["header"])
    async def banner(self, ctx, user: discord.User = None):
        if not user:
            user = ctx.author
        
        user = await ctx.bot.fetch_user(user.id)

        if user.banner is None:
            return await ctx.send(f"{user.mention} não possui um banner definido!")

        avatar_banner_url = user.banner.url 

        embed = default.DefaultEmbed.create(
            title=f"Banner de {user}"
        )
        embed.set_image(url=avatar_banner_url)
        await ctx.send(embed=embed)

    @commands.command(name="dicio", help="Mostra o significado de uma palavra", aliases=["dicionario", "search"])
    async def dicio(self, ctx, *, palavra: str):
        async with aiohttp.ClientSession() as session:
            search_url = f"https://www.dicio.com.br/pesquisa.php?q={quote(palavra)}"
            async with session.get(search_url) as resp:
                if resp.status == 404:
                    return await ctx.send(content="❌ Palavra não encontrada.")
                html = await resp.text()
                
        soup = BeautifulSoup(html, "html.parser")
        
        resultados = soup.find("ul", class_="resultados")
        if resultados:
            first_li = resultados.find("li")
            if not first_li:
                return await ctx.send(content="❌ Palavra não encontrada.")
            
            link = first_li.find("a", class_="_sugg")["href"]
            async with session.get("https://www.dicio.com.br" + link) as resp:
                html = await resp.text()

            soup = BeautifulSoup(html, "html.parser")
            
            description = soup.select_one("p.significado")
            if description is None or description.text.startswith("Ainda não temos o significado"):
                return await ctx.send(content="❌ Palavra não encontrada.")

            word_title = soup.find("h1").text
            spans = description.find_all("span")
            tipo = spans[0].text if len(spans) >= 1 else ""
            significado = spans[1].text if len(spans) >= 2 else description.text

            frase_tag = soup.find(class_="frase")
            frase = frase_tag.text.strip() if frase_tag else "Nenhum exemplo encontrado."

            embed = discord.Embed(
                title=f"📘 {word_title}",
                description=f"*{tipo}*\n{significado}",
                color=discord.Color.from_rgb(25, 89, 132)
            )
            embed.add_field(name="🖋 Exemplo", value=frase, inline=False)

            await ctx.send(embed=embed)

async def setup(bot):
    print(f"⚙️ Configurando cog Utilidades...")
    await bot.add_cog(Utilidades(bot))
    print(f"✅ Cog Utilidades adicionado com sucesso!")