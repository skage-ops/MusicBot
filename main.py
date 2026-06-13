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


class MusicControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Pause", emoji="⏸️", style=discord.ButtonStyle.secondary)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            await interaction.response.send_message("❌ Não estou num canal de voz.", ephemeral=True)
            return

        await player.pause(True)
        await interaction.response.send_message("⏸️ Música pausada.", ephemeral=True)

    @discord.ui.button(label="Resume", emoji="▶️", style=discord.ButtonStyle.success)
    async def resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            await interaction.response.send_message("❌ Não estou num canal de voz.", ephemeral=True)
            return

        await player.pause(False)
        await interaction.response.send_message("▶️ Música retomada.", ephemeral=True)

    @discord.ui.button(label="Stop", emoji="⏹️", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            await interaction.response.send_message("❌ Não estou num canal de voz.", ephemeral=True)
            return

        await player.stop()
        await interaction.response.send_message("⏹️ Música parada.", ephemeral=True)

    @discord.ui.button(label="Leave", emoji="👋", style=discord.ButtonStyle.secondary)
    async def leave_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            await interaction.response.send_message("❌ Não estou num canal de voz.", ephemeral=True)
            return

        await player.disconnect()
        await interaction.response.send_message("👋 Saí do canal de voz.", ephemeral=True)


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

    await channel.connect(cls=wavelink.Player)

    await ctx.send(f"🔊 Entrei em **{channel.name}**")


@bot.command()
async def play(ctx, *, query: str):
    if not ctx.author.voice:
        await ctx.send("❌ Entra num canal de voz primeiro.")
        return

    if not ctx.voice_client:
        player: wavelink.Player = await ctx.author.voice.channel.connect(
            cls=wavelink.Player
        )
    else:
        player: wavelink.Player = ctx.voice_client

    tracks = await wavelink.Playable.search(query)

    if not tracks:
        await ctx.send("❌ Música não encontrada.")
        return

    if isinstance(tracks, wavelink.Playlist):
        track = tracks.tracks[0]
    else:
        track = tracks[0]

    await player.play(track)

    embed = discord.Embed(
        title="🎵 A tocar agora",
        description=f"**{track.title}**",
        color=discord.Color.blurple()
    )

    await ctx.send(embed=embed, view=MusicControlView())


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