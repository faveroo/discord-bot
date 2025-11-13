from discord.ext import commands
from embed.error import ErrorEmbed
import discord

async def setup_global_error_handler(bot):
    @bot.event
    async def on_command_error(ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        
        if ctx.cog:
            if ctx.cog._get_overridden_method(ctx.cog.cog_command_error) is not None:
                return
        
        if isinstance(error, commands.MissingRequiredArgument):
            embed = ErrorEmbed.create(
                title="❌ Argumento faltando",
                description=f"Verifique os argumentos com `{ctx.prefix}help {ctx.command}`.",
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.CommandNotFound):
            return