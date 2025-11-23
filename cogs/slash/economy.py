import discord
from database import get_currency, set_currency, set_last_daily, get_last_daily
from discord import app_commands
from discord.ext import commands

class EconomySlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="saldo", description="💰 Veja seu saldo atual ou o de outro usuário.")
    async def saldo(self, interaction: discord.Interaction, member: discord.Member = None):
        await interaction.response.defer()

        user = member or interaction.user
        saldo_atual = await get_currency(user)

        embed = discord.Embed(
            title=f"Saldo de {user.display_name}",
            description=f"💰 {user.mention} tem **{saldo_atual:,}** moedas.",
            color=discord.Color.green()
        )

        await interaction.followup.send(embed=embed)
        
async def setup(bot):
    await bot.add_cog(EconomySlash(bot))