import json
import random
import asyncio
import httpx
import aiohttp
import os
import discord
from zoneinfo import ZoneInfo
from handlers.economy_errors import EconomyError
from discord import app_commands
from bson import ObjectId
from helpers.time_converter import parse_time
from datetime import datetime, timedelta, timezone
BR_TZ = timezone(timedelta(hours=-3))
from database import set_localizacao, get_localizacao, remove_localizacao, create_reminder, edit_reminder_message, delete_reminder, get_user_reminders, get_pending_reminders, find_reminder_by_prefix
from views.cotacao_view import CotacaoView
from bs4 import BeautifulSoup
from embed import error, success, default, info
from deep_translator import GoogleTranslator
from discord.ext import commands
from urllib.parse import quote
from dotenv import load_dotenv

class Utilidades(commands.Cog, name="Utilidades"):
    """Comandos úteis e informativos"""

    def __init__(self, bot):
        self.bot = bot
        self._tasks = {}
        print(f"✅ Cog Utilidades inicializado com os comandos: {[c.name for c in self.get_commands()]}")

    async def cog_load(self):
        asyncio.create_task(self._load_pending())

    async def _load_pending(self):
        await self.bot.wait_until_ready()
        docs = await get_pending_reminders()

        now = datetime.now(timezone.utc)
        for doc in docs:
            remind_at: datetime = doc["remind_at"]
            delta = (remind_at - now).total_seconds()
            if delta < 0:
                delta = 0

            t = asyncio.create_task(self._schedule(doc["_id"], delta))
            self._tasks[str(doc["_id"])] = t
    
    async def _schedule(self, reminder_id: ObjectId, seconds: float):
        try:
            await asyncio.sleep(seconds)
        except asyncio.CancelledError:
            return

        from database import reminders

        doc = await reminders.find_one({"_id": reminder_id})
        if not doc:
            return

        user = self.bot.get_user(doc["user_id"]) or await self.bot.fetch_user(doc["user_id"])
        embed = default.DefaultEmbed.create(
            title="🔔 Lembrete",
            description=doc["message"]
        )

        try:
            await user.send(embed=embed)
        except:
            channel = self.bot.get_channel(doc["channel_id"])
            if channel:
                await channel.send(f"{user.mention}", embed=embed)
        await delete_reminder(reminder_id)
        self._tasks.pop(str(reminder_id), None)

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
                return await ctx.send(embed=error.ErrorEmbed.create(
                    title="❌ Erro",
                    description=f"Erro ao obter conselho: {e}"
                ))

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
            await ctx.send(embed=error.ErrorEmbed.create(
                title="❌ Erro",
                description="Por favor, especifique o que você quer ver. Use `!help ver` para mais informações."
            ))

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

    @ver.command(name="moeda", help="Mostra a moeda de um país")
    async def moeda(self, ctx, *, pais: str):
        """Mostra a moeda de um país"""
        with open('json/capitais.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pais = pais.strip().title()
        info = data.get(pais)

        if info:
            moeda = info['moeda']
            await ctx.send(embed=default.DefaultEmbed.create(
                title=f"🌍 **{pais.capitalize()}**",
                description=f"💰 Moeda: {moeda}\n"
            ))
        else:
            await ctx.send(embed=error.ErrorEmbed.create(
                title="❌ Erro",
                description="País não encontrado! Verifique se escreveu corretamente."
            ))

    @commands.command(name="rps", help="Jogo Pedra, Papel ou Tesoura", aliases=["paperrock", "papelpedra", "rockpaperscissors"])
    async def rps(self, ctx, escolha: str, amount: int = 0):
        from database import get_currency, update_currency
        escolhas_validas = ["pedra", "papel", "tesoura"]
        escolha = escolha.lower()
        if escolha not in escolhas_validas:
            return await ctx.send(embed=error.ErrorEmbed.create(title="❌ Erro", description="Escolha inválida! Use 'pedra', 'papel' ou 'tesoura'."))

        saldo_atual = await get_currency(ctx.author)
        if amount <= 0:
            return await EconomyError.InvalidAmount(ctx)
        if saldo_atual < amount:
            return await EconomyError.NotEnoughMoney(ctx)
        
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

    @commands.guild_only()
    @commands.command(name="userinfo", help="Mostra informações do usuário", aliases=["user"])
    async def userinfo(self, ctx, user: discord.User = None):
        if not user:
            user = ctx.author

        member = ctx.guild.get_member(user.id)
        
        embed = default.DefaultEmbed.create(
            title=f"Informações do usuário {user}"
        )

        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)

        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Nome", value=user.name, inline=True)
        embed.add_field(
            name="Criado em",
            value=user.created_at.strftime("%d/%m/%Y %H:%M:%S"),
            inline=True
        )

        if member:
            embed.add_field(
                name="Entrou no servidor em",
                value=member.joined_at.strftime("%d/%m/%Y %H:%M:%S"),
                inline=True
            )
            embed.add_field(name="Status", value=str(member.status).title(), inline=True)
            embed.add_field(
                name="Atividade",
                value=member.activity.name if member.activity else "Nenhuma",
                inline=True
            )
        else:
            embed.add_field(name="Entrou no servidor em", value="Usuário não está no servidor", inline=True)
            embed.add_field(name="Status", value="Indisponível", inline=True)
            embed.add_field(name="Atividade", value="Indisponível", inline=True)

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

            h1 = soup.find("h1")
            word_title = "".join(h1.find_all(string=True, recursive=False)).strip()
            spans = description.find_all("span")
            significado = spans[1].text if len(spans) >= 2 else description.text

            frase_tag = soup.find(class_="frase")
            frase = frase_tag.text.strip() if frase_tag else "Nenhum exemplo encontrado."

            embed = default.DefaultEmbed.create(
                title=f"📘 Definição de {word_title.capitalize()}",
                description=f"{significado}",
            )
            embed.add_field(name="Exemplo: ", value=frase, inline=True)

            await ctx.send(embed=embed)

    @commands.group(help="Grupo com relação comandos local", hidden=True)
    async def local(self, ctx):
        """Comandos para definir, ver ou excluir o local"""
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=error.ErrorEmbed.create(
                title="❌ Erro",
                description="Digite `!help local` para saber mais!"
            ))

    @local.command(name="set", help="Define sua cidade/localização para comandos futuros")
    async def set_local(self, ctx, *, cidade: str):
        await set_localizacao(ctx.author, cidade)
        embed = success.SuccessEmbed.create(
            title="Localização definida com sucesso",
            description=f"{ctx.author.mention} sua localização foi definida como **{cidade}**"
        )
        await ctx.send(f"✅ Localização de {ctx.author.mention} definida como: **{cidade}**")
        
    @local.command(name="get", help="Mostra o local difinido pelo usuário")
    async def get_local(self, ctx):
        loc = await get_localizacao(ctx.author)
        embed = default.DefaultEmbed.create(
            title="Localização do Usuário",
            description=f"**Localização:** {loc}"
        )

        await ctx.send(embed=embed)
    
    @local.command(name="remove", help="Remove o local definido")
    async def remove_local(self, ctx):
        loc = await get_localizacao(ctx.author)

        if not loc:
            embed = error.ErrorEmbed.create(
                title="❌ Você não possui local definido"
            )
            return await ctx.send(embed=embed)
        
        if await remove_localizacao(ctx.author):
            embed = success.SuccessEmbed.create(
                title="✅ Localização removida com sucesso"
            )
            return await ctx.send(embed=embed)

    @commands.command(name="temperatura", help="Mostra a temperatura de um local em ºC", aliases=["temp", "temperature", "openWeather"])
    async def temperatura(self, ctx, *, local: str = None):
        if not local:
            local = await get_localizacao(ctx.author)
            if not local:
                return await ctx.send("Use `!local set <local>` para definir seu local ou especifique ao executar o comando")
        load_dotenv()
        weather = os.getenv("WEATHER_KEY")
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={quote(local)}&limit={1}&appid={weather}"

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(geo_url)
                resp.raise_for_status()
                geo_data = resp.json()
            except httpx.HTTPStatusError:
                return await ctx.send(embed=error.ErrorEmbed.create(
                    title="❌ Erro",
                    description=f"Não foi possível encontrar informações para **{local}**."
                ))
            except Exception as e:
                return await ctx.send(embed=error.ErrorEmbed.create(
                    title="❌ Erro",
                    description=f"Erro ao consultar o clima: {e}"
                ))
            
            if not geo_data:
                return await ctx.send(embed=error.ErrorEmbed.create(
                    title="❌ Erro",
                    description=f"Cidade **{local}** não encontrada."
                ))
        
            lat = geo_data[0]['lat']
            lon = geo_data[0]['lon']
            
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather}&units=metric&lang=pt"
            
            try:
                weather_resp = await client.get(weather_url)
                weather_resp.raise_for_status()
                weather_data = weather_resp.json()
            except Exception as e:
                return await ctx.send(embed=error.ErrorEmbed.create(
                    title="❌ Erro",
                    description=f"Erro ao buscar clima: {e}"
                ))

        cidade_nome = weather_data["name"]
        pais = weather_data["sys"]["country"]
        temp = weather_data["main"]["temp"]
        descricao = weather_data["weather"][0]["description"].capitalize()
        icon_code = weather_data["weather"][0]["icon"]
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        humidade = weather_data["main"]["humidity"]

        embed = discord.Embed(
            title=f"🌡 Clima em {cidade_nome}, {pais}",
            description=descricao,
            color=discord.Color.from_rgb(25, 89, 132)
        )
        embed.add_field(name="🌡 Temperatura", value=f"{temp}°C", inline=True)
        embed.add_field(name="💧 Humidade", value=f"{humidade}%", inline=True)
        embed.set_thumbnail(url=icon_url)
        await ctx.send(embed=embed)

    @commands.command(name="cotacao", help="Pega a cotação atual do dolar em relação ao real")
    async def cotacao(self, ctx, *, moeda: str = None):
        if moeda and len(moeda.split()) > 1:
            return await ctx.send(embed=error.ErrorEmbed.create(
                title="❌ Erro",
                description="Use apenas **1 moeda por vez**."
            ))

        if moeda is None:
            moedas = ["USD", "EUR", "BTC"]
            m = "USD-BRL,EUR-BRL,BTC-BRL"
        else:
            moedas = [moeda.upper()]
            m = f"{moeda.upper()}-BRL"
        load_dotenv()
        awesome = os.getenv("AWESOME_TOKEN")
        url = f"https://economia.awesomeapi.com.br/last/{m}?token={awesome}"
        
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            
        try:
            dados = r.json()
            print("DEBUG:", dados)
        except Exception:
            embed = error.ErrorEmbed.create(
                title="❌ Erro ao acessar a API",
                description=f"Foi retornada uma resposta inválida.\n\nStatus: {r.status_code}"
            )
            return await ctx.send(embed=embed)

        embeds = []
        for moeda in moedas:
            key = f"{moeda}BRL"
            if key not in dados:
                embed = error.ErrorEmbed.create(
                    title="❌ Moeda não encontrada",
                    description=f"A moeda **{moeda}** não existe ou não foi encontrada.",
                )
                embeds.append(embed)
                continue
            
            info = dados[key]
            embed = default.DefaultEmbed.create(
                title=f"💱 Cotação {moeda}/BRL",
            )
            embed.add_field(name="💰 Valor atual", value=f"R$ {info['bid'].replace(".", ",")}")
            embed.add_field(name="📈 Alta", value=f"R$ {info['high'].replace(".", ",")}")
            embed.add_field(name="📉 Baixa", value=f"R$ {info['low'].replace(".", ",")}")
            embed.set_footer(text="Dados por AwesomeAPI")
            embeds.append(embed)
            
        if len(embeds) == 1:
            return await ctx.send(embed=embeds[0])
        
        view = CotacaoView(ctx, embeds)
        await ctx.send(embed=embeds[0], view=view)
        
    @commands.group(name="remind", help="Comandos de lembrete", aliases=["lembrete", "lembrar"])
    async def remind(self, ctx):
        """Comandos para criar, listar, excluir ou editar lembretes"""
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=error.ErrorEmbed.create(
                title="❌ Erro",
                description="Digite `!help remind` para saber mais!"
            ))

    @remind.command(name="set", help="Cria um lembrete", aliases=["criar"])
    async def remind_set(self, ctx, time: str, *, message: str):
        seconds = parse_time(time)
        if not seconds:
            return await ctx.send(embed=error.ErrorEmbed.create(
                title="❌ Tempo inválido",
                description="Use: 10s, 5m, 2h30m, 1d"
            ))
        
        remind_at = datetime.now(timezone.utc) + timedelta(seconds=seconds)

        oid = await create_reminder(
            user_id=ctx.author.id,
            message=message,
            remind_at=remind_at,
            channel_id=ctx.channel.id
        )

        task = asyncio.create_task(self._schedule(oid, seconds))
        self._tasks[str(oid)] = task

        remind_at_br = remind_at.astimezone(BR_TZ)

        embed = success.SuccessEmbed.create(title="⏰ Lembrete criado!")
        embed.set_footer(text=f"Será lembrado em {remind_at_br.strftime('%d/%m/%Y %H:%M:%S')} (BR)")
        await ctx.send(embed=embed)
    
    @remind.command(name="list", help="Lista os lembretes", aliases=["listar"])
    async def remind_list(self, ctx):
        reminders = await get_user_reminders(ctx.author.id)

        if not reminders:
            embed = info.InfoEmbed.create(
                title=f"📪 Você não tem lembretes"
            )
            return await ctx.send(embed=embed)
        
        embed = default.DefaultEmbed.create(
            "📫 Seus lembretes"
        )

        for r in reminders:

            remind_at_br = r["remind_at"].astimezone(BR_TZ)

            embed.add_field(
                name=f"ID: `{str(r['_id'])[:6]}`",
                value=( 
                    f"📌 {r['message']}\n"
                    f"⏰ {remind_at_br.strftime('%d/%m/%Y %H:%M:%S')} BR",
                ),
                inline=False
            )
        
        await ctx.send(embed=embed)

    @remind.command(name="edit")
    async def remind_edit(self, ctx, reminder_prefix: str, *, new_message: str):
        """Edita a mensagem de um lembrete"""
        doc = await find_reminder_by_prefix(ctx.author.id, reminder_prefix)

        if not doc:
            return await ctx.send(embed=error.ErrorEmbed.create(
                title="❌ Lembrete não encontrado"
            ))

        await edit_reminder_message(doc["_id"], new_message)
    
        await ctx.send(embed=success.SuccessEmbed.create(
            title="✏️ Mensagem do lembrete atualizada!"
        ))

    @remind.command(name="remove")
    async def remind_remove(self, ctx, reminder_prefix: str):
        """Remove um lembrete"""
        doc = await find_reminder_by_prefix(ctx.author.id, reminder_prefix)
        if not doc:
            return await ctx.send(embed=error.ErrorEmbed.create(
                title="❌ Lembrete não encontrado"
            ))

        t = self._tasks.pop(str(doc["_id"]), None)
        if t:
            t.cancel()

        await delete_reminder(doc["_id"])

        await ctx.send(embed=default.DefaultEmbed.create(
            title="🗑️ Lembrete removido."
        ))

    @commands.command(name="calculator", help="Calcula uma expressão matemática, ex: !calc 2+2", aliases=["calc"])
    async def calculator(self, ctx, *, expression: str):
        try:
            result = eval(expression)
        except Exception as e:
            return await ctx.send(embed=error.ErrorEmbed.create(
                title="❌ Erro",
                description=f"Erro ao calcular a expressão"
            ))
        
        await ctx.send(embed=default.DefaultEmbed.create(
            title="🧮 Calculadora",
            description=f"**Expressão:** {expression}\n**Resultado:** {result}"
        ))
    

async def setup(bot):
    print(f"⚙️ Configurando cog Utilidades...")
    await bot.add_cog(Utilidades(bot))
    print(f"✅ Cog Utilidades adicionado com sucesso!")