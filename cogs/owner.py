from embed import error, success, default
import discord
from discord.ext import commands
from discord import app_commands

class Owner(commands.Cog, name="Owner"):
    @commands.is_owner()
    @commands.command(name="setbalance", help="Definir o saldo de um usuário (Admin apenas)", aliases=["set saldo", "set money"], hidden=True)
    async def set_saldo(self, ctx, member: discord.Member, amount: int):
        
        from database import set_currency
        await set_currency(member, amount)

        embed = success.SuccessEmbed.create(
            title="Saldo Definido", 
            description=f"💰 O saldo de {member.mention} foi definido para {amount} moedas.", 
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Owner(bot))