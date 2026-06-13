import os
import discord
import wavelink
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user} está online!")

    host = os.getenv("LAVALINK_HOST")
    port = os.getenv("LAVALINK_PORT")
    password = os.getenv("LAVALINK_PASSWORD")
    secure = os.getenv("LAVALINK_SECURE") == "true"

    protocolo = "https" if secure else "http"
    uri = f"{protocolo}://{host}:{port}"

    node = wavelink.Node(uri=uri, password=password)

    try:
        await wavelink.Pool.connect(client=bot, nodes=[node])
        print("✅ Ligado ao Lavalink!")
    except Exception as erro:
        print(f"❌ Erro ao ligar ao Lavalink: {erro}")


@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")


@bot.command()
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.send("❌ Tens de estar num canal de voz.")
        return

    canal = ctx.author.voice.channel

    if ctx.voice_client:
        await ctx.voice_client.move_to(canal)
    else:
        await canal.connect(self_deaf=True, timeout=60)

    await ctx.send(f"🔊 Entrei em **{canal.name}**")


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Saí do canal de voz.")
    else:
        await ctx.send("❌ Não estou em nenhum canal de voz.")


@bot.command()
async def play(ctx, *, search: str):
    if ctx.author.voice is None:
        await ctx.send("❌ Tens de estar num canal de voz.")
        return

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect(self_deaf=True, timeout=60)

    try:
        if "open.spotify.com" in search:
            tracks = await wavelink.Playable.search(search)
        elif "youtube.com" in search or "youtu.be" in search:
            tracks = await wavelink.Playable.search(search)
        else:
            tracks = await wavelink.Playable.search(f"ytsearch:{search}")

        if not tracks:
            await ctx.send("❌ Não encontrei essa música.")
            return

        if isinstance(tracks, wavelink.Playlist):
            track = tracks.tracks[0]
        else:
            track = tracks[0]

        player = ctx.voice_client

        await player.play(track)

        await ctx.send(f"🎵 A tocar agora: **{track.title}**")

    except Exception as erro:
        await ctx.send(f"❌ Erro ao tocar música: `{erro}`")
        print("ERRO PLAY:", erro)


@bot.command()
async def pause(ctx):
    player = ctx.voice_client

    if not player:
        await ctx.send("❌ Não estou num canal de voz.")
        return

    if hasattr(player, "pause"):
        await player.pause(True)
        await ctx.send("⏸️ Música pausada.")
    else:
        await ctx.send("❌ Este player não suporta pause neste modo.")


@bot.command()
async def resume(ctx):
    player = ctx.voice_client

    if not player:
        await ctx.send("❌ Não estou num canal de voz.")
        return

    if hasattr(player, "pause"):
        await player.pause(False)
        await ctx.send("▶️ Música retomada.")
    else:
        await ctx.send("❌ Este player não suporta resume neste modo.")


@bot.command()
async def stop(ctx):
    player = ctx.voice_client

    if not player:
        await ctx.send("❌ Não estou num canal de voz.")
        return

    if hasattr(player, "stop"):
        await player.stop()
        await ctx.send("⏹️ Música parada.")
    else:
        await ctx.send("❌ Este player não suporta stop neste modo.")


@bot.command()
async def skip(ctx):
    player = ctx.voice_client

    if not player:
        await ctx.send("❌ Não estou num canal de voz.")
        return

    if hasattr(player, "stop"):
        await player.stop()
        await ctx.send("⏭️ Música saltada.")
    else:
        await ctx.send("❌ Este player não suporta skip neste modo.")


bot.run(os.getenv("DISCORD_TOKEN"))