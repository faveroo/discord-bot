import discord
import random
import asyncio
from discord.ext import commands
from handlers.economy_errors import *
from helpers import near
from helpers.parsed_type import parse_bet_type
from embed import error, success, default
from datetime import datetime, timedelta, timezone
from database import get_currency, update_currency, get_last_daily, set_last_daily
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

RED_NUMBERS = {
    1,3,5,7,9,12,14,16,18,
    19,21,23,25,27,30,32,34,36
}

BLACK_NUMBERS = {
    2,4,6,8,10,11,13,15,17,
    20,22,24,26,28,29,31,33,35
}

class Economy(commands.Cog, name="Economia"):
    """Comandos relacionados à economia"""

    def __init__(self, bot):
        self.bot = bot
        self.roullete = {}
    
    # async def finish_roullete(self, ctx):
    #     guild_id = ctx.guild.id

    #     players = self.roullete[guild_id]["players"]

    #     if len(players) <= 1:
    #         await ctx.send(embed=error.ErrorEmbed.create(
    #             title="❌ Erro",
    #             description="A roleta foi cancelada — jogadores insuficientes."
    #         ))
    #         self.roullete.pop(guild_id, None)
    #         return

    #     # Soma total da banca
    #     total = sum(p["amount"] for p in players)
    #     winner = random.choice(players)

    #     await update_currency(winner["user"], total)

    #     # Mensagem final
    #     msg = "🎰 **Roleta Finalizada!**\n\n"
    #     msg += "\n".join([f"• {p['user'].name} apostou {p['amount']}" for p in players])
    #     msg += f"\n\n🎉 **Vencedor:** {winner['user'].mention} ganhou **{total} moedas!**"

    #     await ctx.send(embed=success.SuccessEmbed.create(
    #         title="✅ Roleta Finalizada!",
    #         description=msg
    #     ))

    #     # Limpa a roleta
    #     self.roullete.pop(guild_id, None)

    
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
            return await EconomyError.InvalidTransfer(ctx)
        if amount <= 0:
            return await EconomyError.InvalidAmount(ctx)
        
        from database import get_currency, update_currency
        saldo_atual = await get_currency(ctx.author)
        if saldo_atual < amount:
            return await EconomyError.NotEnoughMoney(ctx)
        
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
            return await EconomyError.DailyError(ctx, last_daily, now)
        
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
                return await EconomyError.InvalidTransfer(ctx)
                
            
            if member is None:
                return await EconomyError.NotFoundUser(ctx)
            
            if value is None or value <= 0:
                return await EconomyError.InvalidAmount(ctx)
                
            user_currency = get_currency(ctx.author)
            enemy_currency = get_currency(member)
            
            if user_currency < value:
                return await EconomyError.NotEnoughMoney(ctx)
                     
            if enemy_currency < value:
                return await EconomyError.NotEnoughMoneyEnemy(ctx)
            
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
                return await EconomyError.Timeout(ctx)

            await ctx.send(f"✔ {ctx.author.display_name} respondeu!\n"
                        f"{member.mention}, agora é sua vez!")

            resposta2 = await wait(member)

            if resposta2[1] is None:
                return await EconomyError.Timeout(ctx)
            
            author, escolha1 = resposta1
            alvo, escolha2 = resposta2
            
            try:
                escolha1 = int(escolha1)
                escolha2 = int(escolha2)
            except ValueError:
                return await EconomyError.InvalidNumber(ctx)
            
            if not (1 <= escolha1 <= 100 and 1 <= escolha2 <= 100):
                return await EconomyError.InvalidNumberRange(ctx, min=1, max=100)
            
            if escolha1 == escolha2:
                return await EconomyError.InvalidNumberRange(ctx, equal=True)

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

    @commands.command(name="roulette", help="Jogo de roleta", aliases=["roleta"])
    async def roulette(self, ctx, bet_type: str, amount: int):
        # Verifica aposta
        parsed = parse_bet_type(bet_type)
        if not parsed:
            return await EconomyError.InvalidBetType(ctx)

        if amount <= 0:
            return await EconomyError.InvalidAmount(ctx)

        user_currency = await get_currency(ctx.author)
        if user_currency < amount:
            return await EconomyError.NotEnoughMoney(ctx)

        await update_currency(ctx.author, -amount)

        result = random.randint(0, 36)
        color = "red" if result in RED_NUMBERS else "black" if result in BLACK_NUMBERS else "green"

        bet_category, value = parsed

        win = False
        multiplier = 0

        # NÚMERO
        if bet_category == "number":
            if result == value:
                win = True
                multiplier = 35

        # COR
        elif bet_category == "color":
            if color == value:
                win = True
                multiplier = 2

        # FAIXAS
        elif bet_category == "range":
            start, end = value
            if start <= result <= end:
                # 1-12 / 13-24 / 25-36 → 3x
                if (start, end) in [(1,12),(13,24),(25,36)]:
                    win = True
                    multiplier = 3
                # 1-18 / 19-36 → 2x
                else:
                    win = True
                    multiplier = 2

        # Resultado da aposta
        if win:
            prize = amount * multiplier
            await update_currency(ctx.author, prize)
            await ctx.send(embed=success.SuccessEmbed.create(
                title="✅ Roleta Finalizada!",
                description=f"🎰 Resultado: **{result} ({color})**\n"
                f"🎉 Você ganhou **{prize} moedas!** (x{multiplier})"
            ))
        else:
            await ctx.send(embed=error.ErrorEmbed.create(
                title="❌ Roleta Finalizada!",
                description=f"🎰 Resultado: **{result} ({color})**\n"
                f"💀 Você perdeu **{amount} moedas!**"
            ))

async def setup(bot):
    await bot.add_cog(Economy(bot))