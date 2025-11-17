import discord
from datetime import date

class InfoEmbed:
    @staticmethod
    def create(title: str, description: str = "", color: discord.Color = discord.Color.blue()) -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text=f"{date.today().year}")
        return embed