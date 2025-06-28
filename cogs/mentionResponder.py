import nextcord
from nextcord.ext import commands
import random
import asyncio
import json
import os
from config import  ALLOWED_USER_IDS  # Import allowed guilds, channels, and user IDs

class MentionResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_responses = self.load_responses("responses.json")
        self.image_folder = 'images'  # Define your image folder path here
        self.audio_folder = 'audio'   # Define your audio folder path here

    def load_responses(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("default_responses", [])

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot:
            return

        # Define trigger phrases
        image_trigger_phrase = "bokettoo said that you should send nudes"
        audio_trigger_phrase = "bokettoo said play some music"



        # Check for image and audio trigger phrases
        if any(trigger in message.content.lower() for trigger in [image_trigger_phrase, audio_trigger_phrase]):
            # Only proceed if user is allowed
            if message.author.id in ALLOWED_USER_IDS:
                if image_trigger_phrase in message.content.lower():
                    image_file = self.get_random_file(self.image_folder, ['.png', '.jpg', '.jpeg', '.gif'])
                    if image_file:
                        await message.delete()
                        await asyncio.sleep(3)
                        await message.channel.send(file=nextcord.File(image_file))
                    else:
                        await message.channel.send("No images available.")

                elif audio_trigger_phrase in message.content.lower():
                    audio_file = self.get_random_file(self.audio_folder, ['.mp3', '.wav'])
                    if audio_file:
                        await message.delete()
                        await asyncio.sleep(3)
                        await message.channel.send(file=nextcord.File(audio_file))
                    else:
                        await message.channel.send("No audio files available.")
            
            # If the user is not allowed, do nothing for image/audio triggers
            return

        # General mention response (without restrictions for ALLOWED_USER_IDS)
        if self.bot.user in message.mentions:
            async with message.channel.typing():
                await asyncio.sleep(5)  # Delay of 5 seconds

            response = random.choice(self.default_responses)
            await message.reply(response)

    def get_random_file(self, folder_path, extensions):
        try:
            files = os.listdir(folder_path)
            files = [file for file in files if any(file.endswith(ext) for ext in extensions)]
            if files:
                return os.path.join(folder_path, random.choice(files))
            else:
                return None
        except Exception as e:
            print(f"Error retrieving files from {folder_path}: {e}")
            return None

def setup(bot):
    bot.add_cog(MentionResponder(bot))
