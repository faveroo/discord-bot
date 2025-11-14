from discord.ext import commands
from embed.error import ErrorEmbed
import discord

async def setup_global_error_handler(bot):
    @bot.event
    async def on_command_error(ctx, error):

        traducao = {
            "Manage Messages": "Gerenciar mensagens",
            "Ban Members": "Banir membros",
            "Kick Members": "Expulsar membros",
            "Moderate Members": "Moderar membros",
            "Manage Guild": "Gerenciar Guilda/Servidor",
        }

        if hasattr(ctx.command, 'on_error'):
            return
        
        if ctx.cog:
            if ctx.cog._get_overridden_method(ctx.cog.cog_command_error) is not None:
                return
        if isinstance(error, commands.MissingPermissions):
            permissoes = [perm.replace('_', ' ').title() for perm in error.missing_permissions]
            lista = ', '.join(traducao.get(p, p) for p in permissoes)
            await ctx.send(f"🚫 Você precisa das permissões: **{lista}** para usar este comando.")
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = ErrorEmbed.create(
                title="❌ Argumento faltando",
                description=f"Verifique os argumentos com `{ctx.prefix}help {ctx.command}`.",
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.CommandNotFound):
            embed = ErrorEmbed.create(
                title="Comando não encontrado",
                description=f"Verifique os comandos com `{ctx.prefix}help`.",
            )
            await ctx.send(embed=embed) 