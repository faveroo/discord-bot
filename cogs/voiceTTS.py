# cogs/voice_cog.py
import discord
from discord.ext import commands
import asyncio
from helpers.tts import TTSQueue

class VoiceTTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tts = TTSQueue(bot)
        self._playback_tasks = {}

    @commands.command(name="entrar")
    async def entrar(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send("Você precisa estar em um canal de voz para eu entrar.")

        channel = ctx.author.voice.channel
        if ctx.voice_client and ctx.voice_client.is_connected():
            return await ctx.send("Já estou em uma call neste servidor.")

        vc = await channel.connect()
        await ctx.send(f"Entrei na call: **{channel.name}**")

        await self.tts.ensure_playing(ctx.guild, vc)

    @commands.command(name="sair")
    async def sair(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send("Não estou em nenhuma call aqui.")

        await vc.disconnect()
        await ctx.send("Saí da call.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.guild is None:
            return
        
        if message.channel.name != "transcrever":
            return

        vc = message.guild.voice_client
        if not vc or not vc.is_connected():
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

def setup(bot):
    bot.add_cog(VoiceTTS(bot))
