import discord
import random
import asyncio
from discord.ext import commands
from handlers.economy_errors import *
from helpers import near
from embed import error, success, default
from datetime import datetime, timedelta, timezone
from database import get_currency, update_currency, get_last_daily, set_last_daily
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

class Economy(commands.Cog, name="Economia"):
    """Comandos relacionados à economia"""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="balance", help="Ver seu saldo atual 💰", aliases=["saldo", "money"])
    async def balance(self, ctx, user: str = None):     
        if user:
            try:
                member = await commands.MemberConverter().convert(ctx, user)
            except commands.MemberNotFound:
                return await EconomyError.NotFoundUser(ctx)
        else:
            member = ctx.author    
        saldo = await get_currency(member)
            

        if member:  # consultando de outra pessoa
            embed = discord.Embed(
                title=f"Saldo de {member.display_name}",
                description=f"💰 {member.mention} tem **{saldo}** moedas.",
                color=discord.Color.green()
            )
        else:  # consultando o próprio saldo
            embed = discord.Embed(
                title="Seu saldo 💰",
                description=f"Você tem **{saldo}** moedas.",
                color=discord.Color.green()
            )

        await ctx.send(embed=embed)

    @commands.command(name="give", help="Dar moedas para outro usuário", aliases=["dar", "transfer"])
    async def give(self, ctx, member: discord.Member = None, amount: int = 0):
        if not member:
            return await EconomyError.NotFoundUser(ctx)

        if member == ctx.author:
            return await ctx.send(embed=error.ErrorEmbed.create(
                title="❌ Erro",
                description="Você não pode transferir moedas para si mesmo."
            ))
        if amount <= 0:
            return await ctx.send(embed=error.ErrorEmbed.create(
                title="❌ Erro",
                description="A quantia não pode ser negativa."
            ))
        
        from database import get_currency, update_currency
        saldo_atual = await get_currency(ctx.author)
        if saldo_atual < amount:
            return await ctx.send(embed=error.ErrorEmbed.create(
                title="❌ Erro",
                description="Você não tem moedas suficientes para essa transferência."
            ))
        await update_currency(ctx.author, -amount)
        await update_currency(member, amount)

        return await ctx.send(embed=success.SuccessEmbed.create(
            title="✅ Transferência Bem-Sucedida",
            description=f"Você transferiu {amount} moedas para {member.mention}."
        ))

    @commands.command(name="top", help="Mostra o ranking dos usuários com mais moedas", aliases=["ranking", "leaderboard"])
    async def top(self, ctx):
        from database import get_top_users
        top_users = await get_top_users(10)
        embed = default.DefaultEmbed.create(
            title="🏆 Ranking de Moedas",
        )
        description = ""

        for idx, user_data in enumerate(top_users, start=1):
            user = await self.bot.fetch_user(user_data['discord_id'])
            if user:
                description += f"**{idx}. {user.name}** - {user_data['saldo']} moedas\n"
            else:
                description += f"**{idx}. Usuário Desconhecido** - {user_data['saldo']} moedas\n"
        embed.description = description
        await ctx.send(embed=embed)
    
    @commands.command(name="daily", help="Resgatar sua recompensa diária de moedas", aliases=["diario"])
    async def daily(self, ctx):
        user = ctx.author
        last_daily = await get_last_daily(user)
        now = datetime.now(timezone.utc)

        if last_daily and (now - last_daily).days < 1:
            next_claim = last_daily + timedelta(days=1)
            time_remaining = next_claim - now
            hours, remainder = divmod(int(time_remaining.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            return await ctx.send(embed=error.ErrorEmbed.create(
                title="❌ Recompensa Diária Já Resgatada",
                description=f"Você já resgatou sua recompensa diária. Tente novamente em {hours}h {minutes}m {seconds}s."
            ))
        
        rewards_amount = random.randint(50, 350)
        await update_currency(user, rewards_amount)
        await set_last_daily(user, now)
        
        embed = success.SuccessEmbed.create(
            title="✅ Recompensa Diária Resgatada!",
            description=f"Você recebeu {rewards_amount} moedas como recompensa diária."
        )
        await ctx.send(embed=embed)
     
    @commands.command(name="bet", help="Aposta com um usuário", aliases=["apostar"])
    async def bet(self, ctx, member: discord.Member = None, value: int = None):
            if member == ctx.author:
                return await ctx.send(embed=error.ErrorEmbed.create(
                    title="❌ Erro",
                    description="Você não pode transferir moedas para si mesmo."
                ))
                
            
            if member is None:
                return await EconomyError.NotFoundUser(ctx)
            
            if value is None or value <= 0:
                return await ctx.send(embed=error.ErrorEmbed.create(
                    title="❌ Valor inválido",
                    description="Use: !bet @usuario 100"
                ))
                
            user_currency = get_currency(ctx.author)
            enemy_currency = get_currency(member)
            
            if user_currency < value:
                return await ctx.send(embed=error.ErrorEmbed.create(
                    title="❌ Erro",
                    description="Você não possui moedas o suficiente"
                ))
                     
            if enemy_currency < value:
                return await ctx.send(embed=error.ErrorEmbed.create(
                    title="❌ Erro",
                    description="O outro usuário não possui moedas o suficiente"
                ))
            
            await ctx.send(f"{ctx.author.mention} e {member.mention}, escolham um número entre 1 e 100!")
            
            async def wait(user):
                def check(msg):
                    return msg.author == user and msg.channel == ctx.channel
                try:
                    msg = await self.bot.wait_for("message", check=check, timeout=30)
                    await ctx.send(f"{user} escolheu {msg.content}")
                    return user, msg.content
                except asyncio.TimeoutError:
                    return user, None
                
            await ctx.send(f"{ctx.author.mention}, envie sua escolha em até **30 segundos**!")

            resposta1 = await wait(ctx.author)

            if resposta1[1] is None:
                return await ctx.send(f"❌ {ctx.author.display_name} não respondeu. A aposta foi cancelada.")

            await ctx.send(f"✔ {ctx.author.display_name} respondeu!\n"
                        f"{member.mention}, agora é sua vez!")

            resposta2 = await wait(member)

            if resposta2[1] is None:
                return await ctx.send(f"❌ {member.display_name} não respondeu. A aposta foi cancelada.")
            
            author, escolha1 = resposta1
            alvo, escolha2 = resposta2
            
            try:
                escolha1 = int(escolha1)
                escolha2 = int(escolha2)
            except ValueError:
                return await ctx.send("❌ Ambos devem digitar apenas números!")
            
            if not (1 <= escolha1 <= 100 and 1 <= escolha2 <= 100):
                return await ctx.send("❌ Os números devem estar entre 1 e 100!")
            
            if escolha1 == escolha2:
                return await ctx.send("❌ Ambos escolheram o mesmo número! Escolham números diferentes.")

            players = {
                escolha1: author,
                escolha2: alvo
            }
            
            rdn = random.randint(1, 100)
            winner, loser = near(escolha1, escolha2, rdn)
            winner_user = players[winner]
            loser_user = players[loser]
            
            await ctx.send(f"🎯 Número sorteado: **{rdn}**\n🏆 O vencedor é: **{winner_user.mention}**!")
            await update_currency(loser_user, -value)
            await update_currency(winner_user, value)
            
async def setup(bot):
    await bot.add_cog(Economy(bot))