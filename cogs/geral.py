import discord
from embed import error, success, default
from datetime import date
from discord.ext import commands
from discord import app_commands

class Geral(commands.Cog, name="Geral"):
    """Comandos gerais do bot"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Diz olá para o usuário", aliases=["hello", "hi", "hey"])
    async def oi(self, ctx):
        await ctx.send("Olá! 👋 Sou um bot em Python!")

    @commands.command(help="Marca everyone")
    async def todos(self, ctx):
        await ctx.send("Bom dia @everyone 👋")

    @app_commands.command(name="number", description="Responde com um número aleatório")
    async def number(self, interaction: discord.Interaction):
        import random
        num = random.randint(1, 100)
        await interaction.response.send_message(f"Seu número aleatório é: {num}")
    
    @commands.command(help="Informações sobre o bot", aliases=["info", "about"])
    async def sobre(self, ctx):
        app_info = await ctx.bot.application_info()
        data_criacao = ctx.bot.user.created_at.strftime("%d/%m/%Y %H:%M:%S")
        owner = app_info.owner
        embed = default.DefaultEmbed.create(
            title="🤖 Sobre o Bot",
            description="Olá! Eu sou o **Rodolfo**, um bot do Discord criado para ajudar você com várias tarefas e comandos divertidos!\n\n"
            "Aqui estão algumas informações sobre mim:",
        )
        embed.set_thumbnail(url=app_info.icon.url if app_info.icon else ctx.bot.user.display_avatar.url)
        
        embed.add_field(name="Data de Criação", value=f"{data_criacao}", inline=False)
        embed.add_field(name="👑 Desenvolvedor", value=f"{owner.name}", inline=True)
        embed.add_field(name="🌐 Público?", value="✅ Sim" if app_info.bot_public else "🔒 Não", inline=True)
        
        embed.set_footer(text=f"{date.today().year} Rodolfo Bot ©")
        await ctx.send(embed=embed)
        
async def setup(bot):
    await bot.add_cog(Geral(bot))
