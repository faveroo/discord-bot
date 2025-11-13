import discord
from embed import error, info, default, success
from discord.ext import commands

class ModLog(commands.Cog):
    """"Registro de moderação"""
    
    def __init__(self, bot):
        self.bot = bot
        self.log_channels = {} # {guild_id: channel_id}
    
    @commands.has_permissions(manage_guild=True)
    @commands.command(name="setmodlog", help="Define o canal de log")
    async def set_modlog(self, ctx, channel: discord.TextChannel):
        self.log_channels[ctx.guild.id] = channel.id
        await ctx.send(f"✅ Mod-log definido com sucesso")
    
    @commands.has_permissions(manage_guild=True)
    @commands.command(name="showmodlog", help="Mostra o canal configurado para o Mod-log")
    async def show_modlog(self, ctx):
        channel_id = self.log_channels.get(ctx.guild.id)
        if not channel_id:
            return await ctx.send("⚠️ Nenhum canal configurado")
        
        channel = self.bot.get_channel(channel_id)
        await ctx.send(f"Canal de log atual: {channel.mention}")
        
    async def send_log(self, guild: discord.Guild, embed: discord.Embed):
        """"Envia um embed de log"""
        channel_id = self.log_channels.get(guild.id)
        
        if not channel_id:
            return
        
        channel = guild.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = info.InfoEmbed.create(
            title="👢 Usuário Expulso",
            description=f"**Usuário:** {member} - {member.id}"
        )
        await self.send_log(member.guild, embed)
        
async def setup(bot):
    await bot.add_cog(ModLog(bot))