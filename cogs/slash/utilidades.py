import discord
import os
import httpx
from urllib.parse import quote
from dotenv import load_dotenv
from database import get_localizacao
from discord import app_commands
from discord.ext import commands

class UtilidadesSlash(commands.Cog):
    @app_commands.command(name="clima", description="Mostra a temperatura de um local")
    @app_commands.describe(local="Cidade ou local desejado")
    async def temperatura_slash(self, interaction: discord.Interaction, local: str = None):

        await interaction.response.defer()

        if not local:
            local = await get_localizacao(interaction.user)
            if not local:
                return await interaction.followup.send(
                    "❌ Use `/local set <local>` para definir seu local padrão ou especifique um lugar no comando."
                )

        load_dotenv()
        weather = os.getenv("WEATHER_KEY")

        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={quote(local)}&limit=1&appid={weather}"

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(geo_url)
                resp.raise_for_status()
                geo_data = resp.json()
            except Exception:
                return await interaction.followup.send(f"❌ Não foi possível encontrar informações para **{local}**.")

            if not geo_data:
                return await interaction.followup.send(f"❌ Cidade **{local}** não encontrada.")

            lat = geo_data[0]['lat']
            lon = geo_data[0]['lon']

            weather_url = (
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?lat={lat}&lon={lon}&appid={weather}&units=metric&lang=pt"
            )

            try:
                weather_resp = await client.get(weather_url)
                weather_resp.raise_for_status()
                weather_data = weather_resp.json()
            except Exception as e:
                return await interaction.followup.send(f"❌ Erro ao buscar clima: {e}")

        cidade_nome = weather_data["name"]
        pais = weather_data["sys"]["country"]
        temp = weather_data["main"]["temp"]
        descricao = weather_data["weather"][0]["description"].capitalize()
        icon_code = weather_data["weather"][0]["icon"]
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        humidade = weather_data["main"]["humidity"]

        embed = discord.Embed(
            title=f"🌡 Clima em {cidade_nome}, {pais}",
            description=descricao,
            color=discord.Color.from_rgb(25, 89, 132)
        )
        embed.add_field(name="🌡 Temperatura", value=f"{temp}°C", inline=True)
        embed.add_field(name="💧 Humidade", value=f"{humidade}%", inline=True)
        embed.set_thumbnail(url=icon_url)

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UtilidadesSlash(bot))