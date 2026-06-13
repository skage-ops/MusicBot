import os
import discord
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
    await canal.connect()
    await ctx.send(f"🔊 Entrei em {canal.name}")

    import yt_dlp

@bot.command()
async def play(ctx, url):
    if ctx.author.voice is None:
        await ctx.send("❌ Tens de estar num canal de voz.")
        return

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']

    source = discord.FFmpegPCMAudio(audio_url)
    ctx.voice_client.play(source)

    await ctx.send(f"🎵 A tocar: {info['title']}")

    @bot.command()
    async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Saí do canal de voz.")

bot.run(os.getenv("DISCORD_TOKEN"))