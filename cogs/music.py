import discord
import yt_dlp
import asyncio
from embed import error, default, success, info
from discord import PCMVolumeTransformer
from discord.ext import commands


class Music(commands.Cog, name="Músicas"):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.queues = {}
        self.volume = {}

    async def search_ytdlp_async(self, query, ydl_options):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: self._extract(query, ydl_options))
    
    def _extract(self, query, ydl_options):
        with yt_dlp.YoutubeDL(ydl_options) as ydl:
            return ydl.extract_info(query, download=False)

    def play_next(self, ctx, vc):
        guild_id = ctx.guild.id

        if guild_id not in self.queues or len(self.queues[guild_id]) == 0:
            return

        track = self.queues[guild_id].pop(0)

        raw = discord.FFmpegPCMAudio(
            track["url"],
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options='-vn -filter:a "volume=0.2"',
            executable="bin\\ffmpeg\\ffmpeg.exe"
        )

        source = PCMVolumeTransformer(raw, volume=self.volume.get(guild_id, 0.5))
        vc.play(source, after=lambda e: self.play_next(ctx, vc))

        asyncio.run_coroutine_threadsafe(
            ctx.send(f"▶️ Tocando: **{track['title']}**"),
            self.bot.loop
        )

    @commands.command(name="leave", help="Retira o bot da call", aliases=["sair"])
    async def sair(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send("Não estou em nenhuma call aqui.")

        await vc.disconnect()
        await ctx.send("Saí da call.")

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

        guild_id = ctx.guild.id
        if guild_id not in self.queues:
            self.queues[guild_id] = []

        # adiciona na fila
        self.queues[guild_id].append({
            "url": audio_url,
            "title": title
        })

        if not vc_client.is_playing():
            self.play_next(ctx, vc_client)
        else:
            await ctx.send(f"➕ Adicionado à fila: **{title}**")

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

    @commands.command(name="resume", help="Despausa uma música", aliases=["despausar"])
    async def resume(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send("❌ Você precisa estar conectado em um canal de voz")
        
        vc = ctx.author.voice.channel
        
        voice_client = ctx.guild.voice_client

        if not voice_client:
            return await ctx.send("❌ Não estou conectado a um canal de voz")
        
        if voice_client.is_playing():
            return await ctx.send("❌ A música não está pausada.")

        voice_client.resume()
        return await ctx.send("▶️ Voltando a reproduzir...")

    @commands.command(name="skip", aliases=["next", "pular"])
    async def skip(self, ctx):
        vc = ctx.guild.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send("❌ Não estou conectado a um canal de voz.")

        if not vc.is_playing():
            return await ctx.send("⚠ Nada está tocando.")

        vc.stop()
        await ctx.send("⏭ Pulando...")

    @commands.command(name="stop", aliases=["parar", "end"])
    async def stop(self, ctx):
        vc = ctx.guild.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send("❌ Não estou conectado a um canal de voz.")

        guild_id = ctx.guild.id

        self.queues[guild_id] = []

        vc.stop()

        await ctx.send("🛑 Música parada e fila limpa.")

    @commands.command(name="volume", aliases=["vol"])
    async def volume(self, ctx, *, vol: int = None):
        if vol is None:
            guild_volume = self.volume.get(ctx.guild.id, 0.5)
            guild_volume *= 100

            embed = default.DefaultEmbed.create(
                title=f"O volume atual é: {int(guild_volume)}"
            )
            return await ctx.send(embed=embed)

        if not 0 <= vol <= 200:
            return await ctx.send("O volume deve ser entre 0 e 200.")
        
        guild_id = ctx.guild.id
        self.volume[guild_id] = vol / 100

        vc_client = ctx.voice_client
        if vc_client and vc_client.source:
            vc_client.source.volume = self.volume[guild_id]
        
        await ctx.send(f"🔊 Volume definido para **{vol}%**")
async def setup(bot:commands.Bot):
    await bot.add_cog(Music(bot))