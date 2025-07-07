import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
from yt_dlp import YoutubeDL
import asyncio
import os
import traceback

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}
        self.song_queue = {}
        self.ffmpeg_path = self.find_ffmpeg()

    def find_ffmpeg(self):
        """Attempt to find FFmpeg executable."""
        possible_paths = [
            'C:/FFmpeg/bin/ffmpeg.exe',  # Windows default
            '/usr/bin/ffmpeg',  # Linux default
            '/usr/local/bin/ffmpeg',  # Alternative Linux path
            '/opt/homebrew/bin/ffmpeg',  # macOS Homebrew path
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return 'ffmpeg'  # Fallback to system PATH

    async def connect_to_voice(self, interaction: Interaction):
        """Establish connection to voice channel."""
        if interaction.user.voice is None:
            await interaction.response.send_message("You must be in a voice channel to play music.", ephemeral=True)
            return None

        voice_channel = interaction.user.voice.channel
        guild_id = interaction.guild.id

        try:
            # If already connected, move to the user's channel
            if guild_id in self.voice_clients:
                await self.voice_clients[guild_id].move_to(voice_channel)
                return self.voice_clients[guild_id]
            
            # Connect to the voice channel
            voice_client = await voice_channel.connect()
            self.voice_clients[guild_id] = voice_client
            return voice_client
        except Exception as e:
            await interaction.response.send_message(f"Error connecting to voice channel: {str(e)}", ephemeral=True)
            return None

    async def search_songs(self, query: str):
        """Search for songs using yt-dlp."""
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': True,
            'default_search': 'ytsearch',
        }
        
        results = []
        try:
            with YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(f"ytsearch10:{query}", download=False)['entries']
                for result in search_results:
                    results.append({
                        "title": result.get("title", "Unknown Title"), 
                        "url": result.get("webpage_url", "")
                    })
        except Exception as e:
            print(f"Error searching songs: {traceback.format_exc()}")
        
        return results

    async def get_audio_source(self, url):
        """Retrieve audio source for a given URL."""
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                audio_url = info['url']
                
                return nextcord.FFmpegPCMAudio(
                    audio_url, 
                    executable=self.ffmpeg_path,
                    before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
                )
        except Exception as e:
            print(f"Error getting audio source: {traceback.format_exc()}")
            return None

    @nextcord.slash_command(name="play", description="Play a song in your voice channel.")
    async def play_music(
        self,
        interaction: Interaction,
        song: str = SlashOption(
            description="Name or URL of the song to play",
            autocomplete=True
        )
    ):
        """Main play command with improved error handling."""
        # Check if command is used in a guild
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server, not in DMs.", ephemeral=True)
            return
            
        # Defer the response to allow more time for processing
        await interaction.response.defer(ephemeral=False)

        # Connect to voice channel
        voice_client = await self.connect_to_voice(interaction)
        if not voice_client:
            return

        guild_id = interaction.guild.id
        
        # Initialize queue if not exists
        if guild_id not in self.song_queue:
            self.song_queue[guild_id] = []

        try:
            # Resolve URL if not already a URL
            if not song.startswith(('http://', 'https://')):
                search_results = await self.search_songs(song)
                if not search_results:
                    await interaction.followup.send("No songs found.")
                    return
                song = search_results[0]['url']

            # Get audio source
            audio_source = await self.get_audio_source(song)
            if not audio_source:
                await interaction.followup.send("Could not retrieve audio source.")
                return

            # Add to queue
            title = await self.get_song_title(song)
            self.song_queue[guild_id].append((audio_source, title))

            # If only one song in queue, start playing
            if len(self.song_queue[guild_id]) == 1:
                await self.play_next_song(interaction)
            else:
                await interaction.followup.send(f"Added to queue: {title}")

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")
            print(traceback.format_exc())

    async def get_song_title(self, url):
        """Retrieve song title."""
        try:
            with YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('title', 'Unknown Title')
        except:
            return 'Unknown Title'

    async def play_next_song(self, interaction):
        """Play the next song in the queue."""
        # Check if interaction has guild context
        if not interaction.guild:
            return
            
        guild_id = interaction.guild.id
        
        if not self.song_queue.get(guild_id):
            return

        voice_client = self.voice_clients.get(guild_id)
        if not voice_client:
            return

        # Get next song
        audio_source, title = self.song_queue[guild_id][0]

        def after_playing(error):
            if error:
                print(f"Playback error: {error}")
            
            # Remove the current song from queue
            if guild_id in self.song_queue:
                self.song_queue[guild_id].pop(0)
            
            # Play next song
            if self.song_queue.get(guild_id):
                asyncio.run_coroutine_threadsafe(
                    self.play_next_song(interaction), 
                    self.bot.loop
                )

        try:
            voice_client.play(audio_source, after=after_playing)
            await interaction.followup.send(f"Now playing: {title}")
        except Exception as e:
            await interaction.followup.send(f"Error playing song: {str(e)}")
            print(traceback.format_exc())

    @play_music.on_autocomplete("song")
    async def song_autocomplete(self, interaction: Interaction, query: str):
        """Provide autocomplete suggestions for the song name."""
        if not query:
            await interaction.response.send_autocomplete([])
            return

        results = await self.search_songs(query)
        suggestions = [result["title"] for result in results[:10]]
        await interaction.response.send_autocomplete(suggestions)

    @nextcord.slash_command(name="stop", description="Stop the music and leave the voice channel.")
    async def stop_music(self, interaction: Interaction):
        # Check if command is used in a guild
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server, not in DMs.", ephemeral=True)
            return
            
        guild_id = interaction.guild.id

        if guild_id in self.voice_clients:
            voice_client = self.voice_clients[guild_id]
            # Clear the queue
            self.song_queue[guild_id] = []
            
            # Stop playing and disconnect
            if voice_client.is_playing():
                voice_client.stop()
            
            await voice_client.disconnect()
            
            # Remove from tracked voice clients
            del self.voice_clients[guild_id]
            
            await interaction.response.send_message("Stopped playback and disconnected from voice channel.")
        else:
            await interaction.response.send_message("I am not connected to any voice channel.", ephemeral=True)

    @nextcord.slash_command(name="skip", description="Skip the currently playing song.")
    async def skip_music(self, interaction: Interaction):
        # Check if command is used in a guild
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server, not in DMs.", ephemeral=True)
            return
            
        guild_id = interaction.guild.id

        if guild_id not in self.voice_clients:
            await interaction.response.send_message("I am not connected to any voice channel.", ephemeral=True)
            return

        voice_client = self.voice_clients[guild_id]

        if not voice_client.is_playing():
            await interaction.response.send_message("No song is currently playing.", ephemeral=True)
            return

        # Stop current song
        voice_client.stop()

        # Remove current song from queue
        if guild_id in self.song_queue and self.song_queue[guild_id]:
            self.song_queue[guild_id].pop(0)

        # Play next song if available
        if self.song_queue.get(guild_id):
            await self.play_next_song(interaction)
        else:
            await interaction.response.send_message("No more songs in the queue.")

def setup(bot):
    bot.add_cog(Music(bot))