import discord
from embed import error, info, default, success
from database import get_modlog, set_modlog
from discord.ext import commands

class ModLog(commands.Cog):
    """"Registro de moderação"""
    
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
        
    async def send_log(self, guild: discord.Guild, embed: discord.Embed):
        """"Envia um embed de log"""
        channel_id = await get_modlog(guild.id)
        
        if not channel_id:
            return
        
        channel = guild.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)
    

    async def cog_command_error(self, ctx, error):
        if ctx.command and ctx.command.cog_name != "ModLog":
            return

        traducao = {
            "Manage Guild": "Gerenciar Guilda/Servidor",

        }

        if isinstance(error, commands.MissingPermissions):
            permissoes = [perm.replace('_', ' ').title() for perm in error.missing_permissions]
            lista = ', '.join(traducao.get(p, p) for p in permissoes)
            await ctx.send(f"🚫 Você precisa das permissões: **{lista}** para usar este comando.")       
        else:
            print("aqui")
            raise error
        
async def setup(bot):
    await bot.add_cog(ModLog(bot))