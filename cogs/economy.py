import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

class Economy(commands.Cog, name="Economia"):
    """Comandos relacionados à economia"""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="balance", help="Ver seu saldo atual 💰", aliases=["saldo", "money"])
    async def saldo(self, ctx):
        from database import get_currency

        saldo_atual = await get_currency(ctx.author)
        embed = discord.Embed(title="Seu Saldo", description=f"💰 Você tem {saldo_atual} moedas.", color=discord.Color.green())
        await ctx.send(embed=embed)

    @app_commands.command(name="balance", description="Ver seu saldo atual 💰")
    async def balance(self, interaction: discord.Interaction):
        from database import get_currency

        saldo_atual = await get_currency(interaction.user)
        embed = discord.Embed(title="Seu Saldo", description=f"💰 Você tem {saldo_atual} moedas.", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)
    
async def setup(bot):
    await bot.add_cog(Economy(bot))