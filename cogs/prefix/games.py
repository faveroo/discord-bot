from ast import alias
import json
import random
import asyncio
import discord
from helpers.flags import FLAGS
from helpers.normalize import normalize
from embed import error, success, default, info
from deep_translator import GoogleTranslator
from discord.ext import commands

class Games(commands.Cog, name="Jogos"):
    """Jogos divertidos para ganhar moedas"""

    def __init__(self, bot):
        self.bot = bot
        self.active_quiz = False
        self.flags = {}
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

    @commands.command(name="flags", help="Jogo de acertar bandeiras", aliases=["bandeiras"])
    async def flags(self, ctx):
        guild_id = ctx.guild.id

        # Impede dois jogos por servidor
        if guild_id in self.flags:
            return await ctx.send(embed=info.InfoEmbed.create(
                title="⚠️ Já existe um jogo ativo neste servidor!"
            ))

        self.flags[guild_id] = True
        score = 0

        await ctx.send(embed=default.DefaultEmbed.create(
            title="🌍 Jogo de Bandeiras!",
            description="Você tem **30 segundos totais** para acertar cada bandeira.\n"
                        "Digitando errado não reinicia o tempo!"
        ))

        try:
            while True:
                # Escolhe bandeira
                country, img_url = random.choice(list(FLAGS.items()))

                # Envia a bandeira
                embed = default.DefaultEmbed.create(title="🇺🇳 Qual país é este?")
                embed.set_image(url=img_url)
                await ctx.send(embed=embed)

                def check(m):
                    return m.author.id == ctx.author.id and m.channel == ctx.channel

                # TIMER REAL – começa agora
                timer = asyncio.create_task(asyncio.sleep(30))

                # Enquanto não acertar, fica tentando
                while True:
                    try:
                        # Espera mensagem OU timeout
                        msg_task = asyncio.create_task(self.bot.wait_for("message", check=check))
                        done, pending = await asyncio.wait(
                            {timer, msg_task},
                            return_when=asyncio.FIRST_COMPLETED
                        )

                        # Se o tempo acabou primeiro
                        if timer in done:
                            msg_task.cancel()
                            await ctx.send(embed=error.ErrorEmbed.create(
                                title=f"⏰ Tempo esgotado!\nPontuação final: **{score}**"
                            ))
                            return

                        # Usuário respondeu
                        msg = msg_task.result()
                        resposta = normalize(msg.content)

                        # Acertou → passa p/ próxima
                        if resposta == normalize(country):
                            score += 1
                            await ctx.send(embed=success.SuccessEmbed.create(
                                title=f"🎉 **Correto!** +1 ponto\nPontuação: **{score}**\nPróxima bandeira!"
                            ))
                            # Cancela o timer para a próxima bandeira
                            timer.cancel()
                            break
                        await ctx.send(embed=info.InfoEmbed.create(
                            title="❌ Errado!",
                            description="Tente novamente! A bandeira é a mesma."
                        ))

                    except Exception:
                        # Qualquer erro inesperado → encerra o jogo
                        timer.cancel()
                        raise

        finally:
            self.flags.pop(guild_id, None)

async def setup(bot):
    print(f"⚙️ Configurando cog Games...")
    await bot.add_cog(Games(bot))
    print(f"✅ Cog Games adicionado com sucesso!")