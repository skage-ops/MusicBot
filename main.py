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
    secure = os.getenv("LAVALINK_SECURE", "true").lower() == "true"

    protocol = "https" if secure else "http"

    node = wavelink.Node(
        uri=f"{protocol}://{host}:{port}",
        password=password
    )

    await wavelink.Pool.connect(
        client=bot,
        nodes=[node]
    )

    print("✅ Ligado ao Lavalink!")


@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")


@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("❌ Entra num canal de voz primeiro.")
        return

    channel = ctx.author.voice.channel

    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
        await ctx.send(f"🔊 Mudei para **{channel.name}**")
        return

    await channel.connect(
        cls=wavelink.Player,
        self_deaf=True,
        timeout=60
    )

    await ctx.send(f"🔊 Entrei em **{channel.name}**")


@bot.command()
async def play(ctx, *, query: str):
    if not ctx.author.voice:
        await ctx.send("❌ Entra num canal de voz primeiro.")
        return

    if not ctx.voice_client:
        player: wavelink.Player = await ctx.author.voice.channel.connect(
            cls=wavelink.Player,
            self_deaf=True,
            timeout=60
        )
    else:
        player: wavelink.Player = ctx.voice_client

    try:
        tracks = await wavelink.Playable.search(query)
    except Exception as erro:
        await ctx.send(f"❌ Erro ao procurar música: `{erro}`")
        print("ERRO SEARCH:", erro)
        return

    if not tracks:
        await ctx.send("❌ Música não encontrada.")
        return

    if isinstance(tracks, wavelink.Playlist):
        track = tracks.tracks[0]
    else:
        track = tracks[0]

    await player.play(track)
    await ctx.send(f"🎵 A tocar agora: **{track.title}**")


@bot.command()
async def stop(ctx):
    player: wavelink.Player = ctx.voice_client

    if not player:
        await ctx.send("❌ Não estou num canal de voz.")
        return

    await player.stop()
    await ctx.send("⏹️ Música parada.")


@bot.command()
async def leave(ctx):
    player: wavelink.Player = ctx.voice_client

    if not player:
        await ctx.send("❌ Não estou num canal de voz.")
        return

    await player.disconnect()
    await ctx.send("👋 Saí do canal de voz.")


bot.run(os.getenv("DISCORD_TOKEN"))