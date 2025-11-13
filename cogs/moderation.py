import discord
from discord.ext import commands
from embed import success, error, default

class Moderation(commands.Cog, name="Moderação"):
    """Comandos de Moderação"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="clear", help="Limpa mensagens no canal", aliases=["limpar", "purge"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if amount <= 0:
            return await ctx.send(embed=error.ErrorEmbed.create(
                title="❌ Erro",
                description="O número de mensagens a serem apagadas deve ser maior que zero."
            ))

        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 para incluir o comando
        await ctx.send(embed=success.SuccessEmbed.create(
            title=f"✅ {deleted} Mensagens Apagadas",
        ), delete_after=5)
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if ctx.command and ctx.command.cog_name != "moderation":
            return

        traducao = {
            "Manage Messages": "Gerenciar mensagens",
            "Ban Members": "Banir membros",
            "Kick Members": "Expulsar membros",
            "Moderate Members": "Moderar membros",
        }

        if isinstance(error, commands.MissingPermissions):
            permissoes = [perm.replace('_', ' ').title() for perm in error.missing_permissions]
            lista = ', '.join(traducao.get(p, p) for p in permissoes)
            await ctx.send(f"🚫 Você precisa das permissões: **{lista}** para usar este comando.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("⚠️ Usuário não encontrado.") 
            
        else:
            await self.bot.on_command_error(ctx, error)

async def setup(bot):
    await bot.add_cog(Moderation(bot))