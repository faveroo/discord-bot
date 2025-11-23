# cogs/voice_cog.py
import discord
from discord.ext import commands
import asyncio
from helpers.tts import TTSQueue

class VoiceTTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tts = TTSQueue(bot)

    @commands.command(name="join", aliases=["entrar", "voice"])
    async def entrar(self, ctx):
        if ctx.author.voice.channel is None:
            return await ctx.send("Você precisa estar em um canal de voz para eu entrar.")

        channel = ctx.author.voice.channel
        
        if ctx.voice_client and ctx.voice_client.is_connected():
            return await ctx.send("Já estou em uma call neste servidor.")

        vc = await channel.connect()
        await ctx.send(f"Entrei na call: **{channel.name}**")
        
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.guild is None:
            return
        
        if message.channel.name != "transcrever":
            return

        vc = message.guild.voice_client

        if not vc or not vc.is_connected():
            return

        if vc.is_playing():
            return

        text = message.content.strip()
        if not text:
            return

        if len(text) > 400:
            await message.channel.send(f"{message.author.mention} O texto é muito grande para TTS. Limite: 400 caracteres.")
            return

        try:
            await self.tts.enqueue(message.guild.id, text, voice="pt-BR-AntonioNeural")
        except Exception as e:
            await message.channel.send("Erro ao gerar TTS: " + str(e))
            return

        try:
            await self.tts.ensure_playing(message.guild, vc)
        except Exception as e:
            await message.channel.send("Erro ao tocar áudio: " + str(e))

async def setup(bot):
    await bot.add_cog(VoiceTTS(bot))
