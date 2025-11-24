import discord
from embed import error, info, default, success
from database import get_modlog, set_modlog, get_auditlog, set_auditlog
from discord.ext import commands

class Logs(commands.Cog):
    """Registro de logs"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.has_permissions(manage_guild=True)
    @commands.command(name="setmodlog", help="Define o canal de log", hidden=True)
    async def set_modlog_cmd(self, ctx, channel: discord.TextChannel):
        await set_modlog(ctx.guild.id, channel.id)
        embed = success.SuccessEmbed.create(
            title="✅ Mod-log definido com sucesso"
        )
        await ctx.send(embed=embed)
    
    @commands.has_permissions(manage_guild=True)
    @commands.command(name="showmodlog", help="Mostra o canal configurado para o Mod-log", hidden=True)
    async def show_modlog_cmd(self, ctx):
        channel_id = await get_modlog(ctx.guild.id)
        if not channel_id:
            embed = info.InfoEmbed.create(
                title="⚠️ Nenhum canal configurado"
            )

            return await ctx.send(embed=embed)
        
        channel = self.bot.get_channel(channel_id)
        embed = default.DefaultEmbed.create(
            title=f"Canal de log atual: {channel.mention}"
        )
        await ctx.send(embed=embed)

    @commands.has_permissions(manage_guild=True)
    @commands.command(name="createlog", help="Cria um canal de log", hidden=True)
    async def create_modlog_cmd(self, ctx, category: str, name: str = "mod-log"):

        category_obj = discord.utils.get(ctx.guild.categories, name=category)

        everyone = ctx.guild.default_role

        overwrites = {
            everyone: discord.PermissionOverwrite(send_messages=False, add_reactions=False),
            ctx.guild.me: discord.PermissionOverwrite(send_messages=True)
        }

        if category_obj is None:
            category_obj = await ctx.guild.create_category(name=category)

        await ctx.guild.fetch_channels()

        try:
            created = await ctx.guild.create_text_channel(
                name=name,
                category=category_obj,
                overwrites=overwrites,
                topic="Canal de logs",
                reason="Criando canal via bot"
            )
        except Exception as e:
            return await ctx.send(f"❌ Erro ao criar o canal: `{e}`")

        if created:

            set_modlog(ctx.guild.id, created.id)

            embed = success.SuccessEmbed.create(
                title="✅ Chat criado com sucesso"
            )
            await ctx.send(embed=embed)

    async def send_log(self, guild: discord.Guild, embed: discord.Embed):
        """Envia um embed de log de moderação"""
        channel_id = await get_modlog(guild.id)
        
        if not channel_id:
            return
        
        channel = guild.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)
    
    async def send_audit_log(self, guild: discord.Guild, embed: discord.Embed):
        """Envia um embed de auditlog (logs gerais)"""
        channel_id = await get_auditlog(guild.id)
        
        if not channel_id:
            return
        
        channel = guild.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)
    
    @commands.has_permissions(manage_guild=True)
    @commands.command(name="setauditlog", help="Define o canal de auditlog", hidden=True)
    async def set_auditlog_cmd(self, ctx, channel: discord.TextChannel):
        await set_auditlog(ctx.guild.id, channel.id)
        embed = success.SuccessEmbed.create(
            title="✅ Audit-log definido com sucesso"
        )
        await ctx.send(embed=embed)
    
    @commands.has_permissions(manage_guild=True)
    @commands.command(name="showauditlog", help="Mostra o canal configurado para o Audit-log", hidden=True)
    async def show_auditlog_cmd(self, ctx):
        channel_id = await get_auditlog(ctx.guild.id)
        if not channel_id:
            embed = info.InfoEmbed.create(
                title="⚠️ Nenhum canal configurado"
            )

            return await ctx.send(embed=embed)
        
        channel = self.bot.get_channel(channel_id)
        embed = default.DefaultEmbed.create(
            title=f"Canal de auditlog atual: {channel.mention}"
        )
        await ctx.send(embed=embed)

    @commands.has_permissions(manage_guild=True)
    @commands.command(name="createauditlog", help="Cria um canal de auditlog", hidden=True)
    async def create_auditlog_cmd(self, ctx, category: str, name: str = "audit-log"):

        category_obj = discord.utils.get(ctx.guild.categories, name=category)

        everyone = ctx.guild.default_role

        overwrites = {
            everyone: discord.PermissionOverwrite(send_messages=False, add_reactions=False),
            ctx.guild.me: discord.PermissionOverwrite(send_messages=True)
        }

        if category_obj is None:
            category_obj = await ctx.guild.create_category(name=category)

        await ctx.guild.fetch_channels()

        try:
            created = await ctx.guild.create_text_channel(
                name=name,
                category=category_obj,
                overwrites=overwrites,
                topic="Canal de auditlog",
                reason="Criando canal via bot"
            )
        except Exception as e:
            return await ctx.send(f"❌ Erro ao criar o canal: `{e}`")

        if created:

            await set_auditlog(ctx.guild.id, created.id)

            embed = success.SuccessEmbed.create(
                title="✅ Chat criado com sucesso"
            )
            await ctx.send(embed=embed)
    
    
async def setup(bot):
    await bot.add_cog(Logs(bot))