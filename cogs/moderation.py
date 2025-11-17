import discord
import asyncio
from typing import Union
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
    async def ban(self, ctx, member: Union[discord.Member, discord.User, int], *, reason: str):
        if isinstance(member, int):
            try:
                member = await self.bot.fetch_user(member)
            except:
                return await ctx.send("❌ Não consegui encontrar um usuário com esse ID.")

        elif isinstance(member, discord.User):
            pass

        elif isinstance(member, discord.Member):
            pass

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
                await ctx.guild.ban(member, reason=reason)
                confirm_embed = discord.Embed(
                    title="✅ Banimento efetuado",
                    description=f"{member.mention} foi banido com sucesso.",
                    color=discord.Color.green()
                )
                await ctx.send(embed=confirm_embed)

                if self.modlog:
                    embed = info.InfoEmbed.create(
                        title="👢 Usuário Banido",
                        description=f"**Moderador:** {ctx.author}\n**Usuário:** {member}\n**Motivo:** {reason}"
                    )
                    await self.modlog.send_log(ctx.guild, embed)

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
    
    @commands.command(name="mute", help="Muta um membro por determinado tempo", aliases=["m"])
    @commands.has_permissions(manage_roles=True, mute_members=True)
    async def mute(self, ctx, member: discord.Member, time=10, *, reason):
        guild = ctx.guild

        muted_role = discord.utils.get(guild.roles, name="muted")
        self.muted_role = muted_role

        if not muted_role:
            muted_role = await guild.create_role(name="muted")

            for channel in guild.channels:
                try:
                    await channel.set_permissions(muted_role, send_messages=False, speak=False, add_reactions=False)
                except:
                    pass
        
        await member.add_roles(muted_role, reason=reason)
        if self.modlog:
                    embed = info.InfoEmbed.create(
                        title="👢 Usuário Mutado",
                        description=f"**Moderador:** {ctx.author}\n**Usuário:** {member}\n**Tempo:** {time} Minutos\n**Motivo:** {reason}"
                    )
                    embed.set_thumbnail(url=member.avatar.url)
                    await self.modlog.send_log(ctx.guild, embed)

        await asyncio.sleep(time*60)

        if muted_role in member.roles:
            await member.remove_roles(muted_role)

            embed = info.InfoEmbed.create(
                title=f"{member} foi desmutado"
            )
            embed.set_thumbnail(url=member.avatar.url)

            return await self.modlog.send_log(ctx.guild, embed)

    @commands.command(name="unmute", help="Desmuta um usuário mutado", aliases=["desmutar"])
    @commands.has_permissions(manage_roles=True, mute_members=True)
    async def unmute(self, ctx, member: discord.Member):

        if self.muted_role in member.roles:
            await member.remove_roles(self.muted_role)

            embed = info.InfoEmbed.create(
                title=f"{member} foi desmutado", 
                description="Se comporte para não ser mutado novamente 😡"
            )
            embed.set_thumbnail(url=member.avatar.url)
            await self.modlog.send_log(ctx.guild, embed)

            return await ctx.send(f"{member} foi desmutado")
        
        return await ctx.send(f"{member} não está mutado")

    @commands.command(name="unban", help="Desbane um usuário banido do servidor", aliases=["desbanir"])
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, user_id):
        try:
            user = await ctx.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(f"{user} foi desbanido!")
            embed = default.DefaultEmbed.create(
                title=f"{user} foi desbanido",
                description=f"**Responsável:** {ctx.author}"
            )
            return await self.modlog.send_log(ctx.guild, embed)
        except discord.NotFound:
            await ctx.send("Esse usuário não está banido.")
        except Exception as e:
            await ctx.send(f"Erro: {e}")

        
                      
async def setup(bot):
    print(f"✅ Cog Moderação adicionado com sucesso!")