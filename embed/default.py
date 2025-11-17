import discord
from datetime import date

class DefaultEmbed:
    @staticmethod
    def create(title: str, description: str = "", color: discord.Color = discord.Color.dark_purple()) -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(date.today().year)
        return embed