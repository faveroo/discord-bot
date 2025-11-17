import discord
from datetime import datetime

class DefaultEmbed:
    @staticmethod
    def create(title: str, description: str = "", color: discord.Color = discord.Color.dark_purple()) -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=color)
        return embed