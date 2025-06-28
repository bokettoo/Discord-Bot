import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
from pytube import YouTube
import re

class VoiceControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}

    @nextcord.slash_command(name="connect_vc", description="Connect the bot to a voice channel")
    async def connect_vc(self, interaction: Interaction, channel: nextcord.VoiceChannel = SlashOption(
            name="channel",
            description="The voice channel to connect to",
            required=False
        )):
        await interaction.response.defer(ephemeral=True)

        try:
            if channel is None:
                if interaction.user.voice is None:
                    await interaction.followup.send("You need to be in a voice channel or specify one.", ephemeral=True)
                    return
                channel = interaction.user.voice.channel

            if interaction.guild.voice_client is None:
                voice_client = await channel.connect()
                self.voice_clients[interaction.guild.id] = voice_client
                await interaction.followup.send(f"Connected to {channel.name}", ephemeral=True)
            else:
                await interaction.followup.send("I'm already connected to a voice channel.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Error occurred: {str(e)}", ephemeral=True)

    @nextcord.slash_command(name="play", description="Play audio from a URL")
    async def play(self, interaction: nextcord.Interaction, query: str):
        await interaction.response.defer()
        voice_client = interaction.guild.voice_client
        
        if not voice_client:
            if interaction.user.voice:
                channel = interaction.user.voice.channel
                voice_client = await channel.connect()
            else:
                await interaction.followup.send("You are not in a voice channel!", ephemeral=True)
                return

        url_pattern = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
        is_url = re.match(url_pattern, query)
        
        if is_url:
            youtube_url = query
        else:
            await interaction.followup.send("Please provide a valid YouTube URL.", ephemeral=True)
            return

        try:
            yt = YouTube(youtube_url)
            audio_stream = yt.streams.filter(only_audio=True).first()
            audio_url = audio_stream.url
            audio_name = yt.title

            source = nextcord.FFmpegPCMAudio(executable="/home/container/bin/ffmpeg.exe", source=audio_url)
            voice_client.play(source, after=lambda e: print(f"Player error: {e}") if e else None)
            await interaction.followup.send(f"Playing audio: {audio_name}", ephemeral=True)
        except Exception as e:
            print(f"An error occurred: {e}")
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

    @nextcord.slash_command(name="disconnect_vc", description="Disconnect the bot from the voice channel")
    async def disconnect_vc(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            voice_client = interaction.guild.voice_client
            if voice_client and voice_client.is_connected():
                await voice_client.disconnect()
                self.voice_clients.pop(interaction.guild.id, None)
                await interaction.followup.send("Disconnected from the voice channel.", ephemeral=True)
            else:
                await interaction.followup.send("I'm not connected to any voice channel.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Error occurred: {str(e)}", ephemeral=True)

def setup(bot):
    bot.add_cog(VoiceControl(bot))
