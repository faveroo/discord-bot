import discord
import random
from discord.ext import commands
from embed import error, success, default
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

class Economy(commands.Cog, name="Economia"):
    """Comandos relacionados à economia"""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="balance", help="Ver seu saldo atual 💰", aliases=["saldo", "money"])
    async def balance(self, ctx, member: discord.Member = None):
        from database import get_currency
        target = member or ctx.author
        saldo = await get_currency(target)

        if member:  # consultando de outra pessoa
            embed = discord.Embed(
                title=f"Saldo de {target.display_name}",
                description=f"💰 {target.mention} tem **{saldo}** moedas.",
                color=discord.Color.green()
            )
        else:  # consultando o próprio saldo
            embed = discord.Embed(
                title="Seu saldo 💰",
                description=f"Você tem **{saldo}** moedas.",
                color=discord.Color.green()
            )

        await ctx.send(embed=embed)

    @app_commands.command(name="saldo", description="Ver seu saldo atual 💰")
    async def saldo(self, interaction: discord.Interaction, member: discord.Member = None):
        from database import get_currency
        user = member or interaction.user

        saldo_atual = await get_currency(user)

        embed = discord.Embed(
        title=f"Saldo de {user.display_name}",
        description=f"💰 {user.mention} tem **{saldo_atual}** moedas.",
        color=discord.Color.green()
        )

        await interaction.response.send_message(embed=embed)

    @commands.command(name="give", help="Dar moedas para outro usuário", aliases=["dar", "transfer"])
    async def give(self, ctx, member: discord.Member = None, amount: int = 0):
        if not member:
            return await ctx.send(embed=error.ErrorEmbed.create(
                title="❌ Erro",
                description="Usuário não encontrado."
            ))

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
        from database import get_currency, update_currency, get_last_daily, set_last_daily
        import datetime
        
        user = ctx.author
        last_daily = await get_last_daily(user)
        now = datetime.datetime.now()
        
        if last_daily and (now - last_daily).days < 1:
            next_claim = last_daily + datetime.timedelta(days=1)
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
        
async def setup(bot):
    await bot.add_cog(Economy(bot))