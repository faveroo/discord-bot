import discord
from discord.ext import commands
from embed import success, error, default, info

class Moderation(commands.Cog, name="Moderação"):
    """Comandos de Moderação"""

    def __init__(self, bot):
        self.bot = bot
    
    @property
    def modlog(self):
        return self.bot.get_cog("ModLog")

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
            title=f"✅ {len(deleted) - 1} Mensagens Apagadas",
        ), delete_after=5)
    
    @commands.command(name="kick", help="Expulsa um membro do servidor", aliases=["expulsar", "lowkick"])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str):
        await member.kick(reason=reason)
        await ctx.send(f"Usuário {member.mention} foi punido!")
        
        if self.modlog:
            embed = info.InfoEmbed.create(
                title="👢 Usuário Expulso",
                description=f"**Moderador:** {ctx.author}\n**Usuário:** {member}\n**Motivo:** {reason}"
            )
            await self.modlog.send_log(ctx.guild, embed)
    
    async def cog_command_error(self, ctx, error):
        if ctx.command and ctx.command.cog_name != "Moderação":
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
            raise error

async def setup(bot):
    await bot.add_cog(Moderation(bot))