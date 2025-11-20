import discord
import yt_dlp
import asyncio
from discord.ext import commands


class Music(commands.Cog, name="Músicas"):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    async def search_ytdlp_async(self, query, ydl_options):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: self._extract(query, ydl_options))
    
    def _extract(self, query, ydl_options):
        with yt_dlp.YoutubeDL(ydl_options) as ydl:
            return ydl.extract_info(query, download=False)

    @commands.command(name="play", aliases=["tocar"], usage="<musica>")
    async def play(self, ctx:commands.Context, *, song_query: str):
        
        vc = ctx.author.voice.channel

        if vc is None:
            return await ctx.send("❌ Você deve estar conectado em um canal de voz")
        
        vc_client = ctx.guild.voice_client

        if vc_client is None:
            vc_client = await vc.connect()
        elif vc != vc_client.channel:
            await vc_client.move_to(vc)

        ydl_options = {
            "format": "bestaudio[abr<=96]/bestaudio",
            "noplaylist": True,
            "youtube_include_dash_manifest": False,
            "youtube_include_hls_manifest": False
        }

        query = f"ytsearch1:{song_query}"
        result = await self.search_ytdlp_async(query, ydl_options)
        tracks = result.get("entries", [])

        if tracks is None or len(tracks) == 0:
            return await ctx.send("Não encontrei resultados")

        first_track = tracks[0]
        audio_url = first_track["url"]
        title = first_track.get("title", "Untitled")

        ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn"
        }
        
        source = discord.FFmpegOpusAudio(audio_url, **ffmpeg_options, executable="bin\\ffmpeg\\ffmpeg.exe")

        vc_client.play(source)
        await ctx.send(f"▶️ Tocando: **{title}**")


    @commands.command(name="pause", help="Pausa a música", aliases=["pausar", "p"])
    async def pausar(self, ctx:commands.Context):

        if ctx.author.voice is None:
            return await ctx.send("Você precisa estar em um canal de voz.")

        vc = ctx.author.voice.channel
        
        voice_client = ctx.guild.voice_client

        if not voice_client:
            return await ctx.send("Não estou conectado a um canal de voz.")


        if not voice_client.is_playing():
            return await ctx.send("Não há nada tocando")
        
        if voice_client.is_paused():
            return await ctx.send("O áudio já está pausado")

        voice_client.pause()
        return await ctx.send("⏸️ Pausado")

async def setup(bot:commands.Bot):
    await bot.add_cog(Music(bot))