import discord

class InfoEmbed:
    @staticmethod
    def create(title: str, description: str = "", color: discord.Color = discord.Color.blue()) -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=color)
        return embed