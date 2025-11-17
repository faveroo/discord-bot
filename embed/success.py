import discord
from datetime import date

class SuccessEmbed:
    @staticmethod
    def create(title: str, description: str = "", color: discord.Color = discord.Color.green()) -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text=f"{date.today().year}")
        return embed