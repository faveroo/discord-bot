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
    
    @commands.command(name="ban", help="Bane um membro do servidor", aliases = ["banir", "b"])
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str):
        embed = info.InfoEmbed.create(
            title="🚨 Confirmação de banimento",
            description=f"Tem certeza que deseja banir o membro {member.mention}?"
        )
        embed.add_field(name="Motivo", value=reason, inline=False)
        embed.set_footer(text="Reaja com ✅ para confirmar ou ❌ para cancelar (30s).")

        confirm_msg = await ctx.send(embed=embed)
        try:
            await confirm_msg.add_reaction("✅")
            await confirm_msg.add_reaction("❌")
        except discord.Forbidden:
            await ctx.send("⚠️ Não tenho permissão para adicionar reações aqui.")
            return

        def check(reaction, user):
            return (
                user == ctx.author
                and str(reaction.emoji) in ["✅", "❌"]
                and reaction.message.id == confirm_msg.id
            )
        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)

            if str(reaction.emoji) == "✅":
                await member.ban(reason=reason)
                confirm_embed = discord.Embed(
                    title="✅ Banimento efetuado",
                    description=f"{member.mention} foi banido com sucesso.",
                    color=discord.Color.green()
                )
                await ctx.send(embed=confirm_embed)

            else:
                cancel_embed = discord.Embed(
                    title="❌ Banimento cancelado",
                    description="A ação foi cancelada pelo moderador.",
                    color=discord.Color.orange()
                )
                await ctx.send(embed=cancel_embed)

        except TimeoutError:
            timeout_embed = discord.Embed(
                title="⌛ Tempo esgotado",
                description="Você não reagiu a tempo. Banimento cancelado automaticamente.",
                color=discord.Color.greyple()
            )
            await ctx.send(embed=timeout_embed)
        


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