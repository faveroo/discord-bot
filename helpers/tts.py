# helper/voice.py
import asyncio
import os
import uuid
import discord
from pathlib import Path
import edge_tts
import aiofiles

TMP_DIR = Path("tmp_tts")
TMP_DIR.mkdir(exist_ok=True)

class TTSQueue:
    def __init__(self, bot):
        self.bot = bot
        self._tasks = {}
        self._queues = {}
        self._locks = {}

    def _ensure(self, guild_id):
        if guild_id not in self._queues:
            self._queues[guild_id] = asyncio.Queue()
            self._locks[guild_id] = asyncio.Lock()

    async def enqueue(self, guild_id: int, text: str, voice: str = "pt-BR-AntonioNeural"):
        """
        Enfileira um texto para ser falado na guild.
        Retorna o path do arquivo de áudio gerado (wav).
        """
        self._ensure(guild_id)
        
        mp3_name = f"{uuid.uuid4().hex}.mp3"
        opus_name = f"{uuid.uuid4().hex}.opus"
        
        mp3_path = TMP_DIR / mp3_name
        opus_path = TMP_DIR / opus_name

        await self._generate_edge_tts(text, voice, mp3_path)
        await self._convert_to_opus(mp3_path, opus_path)
        
        try:
            os.remove(mp3_path)
        except Exception:
            pass
        
        await self._queues[guild_id].put(opus_path)
        return opus_path

    async def _generate_edge_tts(self, text: str, voice: str, out_path: Path):
        """
        Usa edge-tts para gerar OGG.
        communicate.save() já escreve o arquivo sozinho.
        """
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(out_path))

    async def _convert_to_opus(self, mp3_path: Path, opus_path: Path):
        """
        Converte MP3 para OPUS usando FFmpeg.
        """
        process = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y",
            "-i", str(mp3_path),
            "-c:a", "libopus",
            str(opus_path),
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await process.wait()

    async def _playback_loop(self, guild, voice_client):
        """
        Loop de reprodução por guild. Deve ser invocado uma vez por conexão.
        """
        guild_id = guild.id
        self._ensure(guild_id)
        
        async with self._locks[guild_id]:
            queue = self._queues[guild_id]
            
            while not voice_client.is_connected():
                await asyncio.sleep(0.3)
                return

            while True:
                try:
                    file_path = await asyncio.wait_for(queue.get(), timeout=300.0)
                except asyncio.TimeoutError:
                    continue

                if not voice_client.is_connected():
                    break

                source = discord.FFmpegOpusAudio(str(file_path), executable="bin/ffmpeg/ffmpeg.exe")
                voice_client.play(source)

                while voice_client.is_playing() or voice_client.is_paused():
                    await asyncio.sleep(0.3)

                try:
                    os.remove(file_path)
                except Exception:
                    pass

    async def ensure_playing(self, guild, voice_client):
        """
        Garante que o loop de reprodução está rodando para esta guild.
        """
        guild_id = guild.id
        self._ensure(guild_id)

        if guild_id in self._tasks:
            task = self._tasks[guild_id]
            if not task.done():
               return  # Já existe loop rodando
            
        # Se já tem uma task rodando para esse lock, não inicia outra.
        # Usamos a presença do lock para serializar; criando uma task que
        # imediatamente tentará adquirir o lock.
        async def _run_loop():
            await self._playback_loop(guild, voice_client)

        # start the loop task without awaiting; the loop will acquire the lock
        self._tasks[guild_id] = asyncio.create_task(_run_loop())
