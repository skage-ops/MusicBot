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

    print("HOST:", host)
    print("PORT:", port)
    print("PASS:", password)
    print("SECURE:", secure)

    protocolo = "https" if secure else "http"
    uri = f"{protocolo}://{host}:{port}"

    print("URI:", uri)

    node = wavelink.Node(
        uri=uri,
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
    if ctx.author.voice is None:
        await ctx.send("❌ Tens de estar num canal de voz.")
        return

    canal = ctx.author.voice.channel

    if ctx.voice_client:
        await ctx.voice_client.move_to(canal)
    else:
        await canal.connect(cls=wavelink.Player)

    await ctx.send(f"🔊 Entrei em **{canal.name}**")


@bot.command()
async def play(ctx, *, search: str):
    if ctx.author.voice is None:
        await ctx.send("❌ Tens de estar num canal de voz.")
        return

    if ctx.voice_client is None:
        player: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    else:
        player: wavelink.Player = ctx.voice_client

    tracks = await wavelink.Playable.search(search)

    if not tracks:
        await ctx.send("❌ Não encontrei essa música.")
        return

    track = tracks[0]

    await player.play(track)

    await ctx.send(f"🎵 A tocar agora: **{track.title}**")


@bot.command()
async def pause(ctx):
    player: wavelink.Player = ctx.voice_client

    if not player:
        await ctx.send("❌ Não estou num canal de voz.")
        return

    await player.pause(True)
    await ctx.send("⏸️ Música pausada.")


@bot.command()
async def resume(ctx):
    player: wavelink.Player = ctx.voice_client

    if not player:
        await ctx.send("❌ Não estou num canal de voz.")
        return

    await player.pause(False)
    await ctx.send("▶️ Música retomada.")


@bot.command()
async def stop(ctx):
    player: wavelink.Player = ctx.voice_client

    if not player:
        await ctx.send("❌ Não estou num canal de voz.")
        return

    await player.stop()
    await ctx.send("⏹️ Música parada.")


@bot.command()
async def skip(ctx):
    player: wavelink.Player = ctx.voice_client

    if not player:
        await ctx.send("❌ Não estou num canal de voz.")
        return

    await player.stop()
    await ctx.send("⏭️ Música saltada.")


@bot.command()
async def leave(ctx):
    player: wavelink.Player = ctx.voice_client

    if not player:
        await ctx.send("❌ Não estou num canal de voz.")
        return

    await player.disconnect()
    await ctx.send("👋 Saí do canal de voz.")


bot.run(os.getenv("DISCORD_TOKEN"))