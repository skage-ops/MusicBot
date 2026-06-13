import os
import discord
import yt_dlp
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user} está online!")


@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")


@bot.command()
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.send("❌ Tens de estar num canal de voz.")
        return

    canal = ctx.author.voice.channel

    if ctx.voice_client is not None:
        await ctx.voice_client.move_to(canal)
    else:
        await canal.connect()

    await ctx.send(f"🔊 Entrei em **{canal.name}**")


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Saí do canal de voz.")
    else:
        await ctx.send("❌ Não estou em nenhum canal de voz.")


@bot.command()
async def play(ctx, *, pesquisa):
    if ctx.author.voice is None:
        await ctx.send("❌ Tens de estar num canal de voz.")
        return

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "default_search": "ytsearch",
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(pesquisa, download=False)

        if "entries" in info:
            info = info["entries"][0]

        audio_url = info["url"]
        title = info.get("title", "Música")

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    source = discord.FFmpegPCMAudio(
        audio_url,
        before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        options="-vn"
    )

    ctx.voice_client.play(source)

    await ctx.send(f"🎵 A tocar: **{title}**")


@bot.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏹️ Música parada.")
    else:
        await ctx.send("❌ Não está nada a tocar.")


@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Música pausada.")
    else:
        await ctx.send("❌ Não está nada a tocar.")


@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Música retomada.")
    else:
        await ctx.send("❌ Não há música pausada.")


bot.run(os.getenv("DISCORD_TOKEN"))