from embed import error, success, default, info
import discord
from database import set_banned_user, get_banned_users, remove_banned_user
from discord.ext import commands
from discord import app_commands

class Owner(commands.Cog, name="Owner"):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.is_owner()
    @commands.command(name="setbalance", help="Definir o saldo de um usuário (Admin apenas)", aliases=["setsaldo", "setmoney"], hidden=True)
    async def set_saldo(self, ctx, member: discord.Member, amount: int):
        
        from database import set_currency
        await set_currency(member, amount)

        embed = success.SuccessEmbed.create(
            title="Saldo Definido", 
            description=f"💰 O saldo de {member.mention} foi definido para {amount} moedas.", 
        )
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command(name="reseteconomy", help="reseta saldo global", hidden=True)
    async def reset_economy(self, ctx):
        from database import reset_economia

        modificados = await reset_economia(150)

        await ctx.send(
            f"🔄 Economia resetada com sucesso!\n"
            f"💰 **{modificados} usuários** agora possuem **150 moedas**."
        )

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("🚫 Apenas o dono do bot pode usar este comando.")
        else:
            raise error

    @commands.is_owner()
    @commands.command(name="rdfunban", aliases=["masterunban"], hidden=True)
    async def rdfunban(self, ctx, user: discord.User):
        banned_users = await get_banned_users()
        banned_list = [u async for u in banned_users]

        if any(u["discord_id"] == user.id for u in banned_list):
            await remove_banned_user(user)
            return await ctx.send(embed=success.SuccessEmbed.create(
                title="✅ Usuário desbanido!"
            ))
        
        return await ctx.send(embed=info.InfoEmbed.create(
            title="⚠️ Usuário não está banido."
        ))

    @commands.is_owner()
    @commands.command(name="rdfban", aliases=["masterban"], hidden=True)
    async def rdfban(self, ctx, user: discord.User):
        banned_users = await get_banned_users()
        banned_list = [u async for u in banned_users]

        if any(u["discord_id"] == user.id for u in banned_list):
            return await ctx.send("❌ Usuário já está banido do bot.")
        
        await set_banned_user(user)
        await ctx.send(f"🔨 {user.mention} foi banido de usar o bot.")

async def setup(bot):
    await bot.add_cog(Owner(bot))