import discord
from discord.ext import commands, tasks
import os
import asyncio
from config import ALLOWED_USER_ID

class ImageSenderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="send")
    async def send_images(self, ctx):
        # Check if the user is allowed
        if ctx.author.id != ALLOWED_USER_ID:
            await ctx.send("You do not have permission to use this command.")
            return
        
        # Path to the directory where images are stored
        folder_path = "download"

        # List all files in the directory
        files = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg','webp', '.gif'))]

        if not files:
            await ctx.send("No images found in the download directory.")
            return

        # Send images with a 5-second delay
        for file in files:
            file_path = os.path.join(folder_path, file)
            with open(file_path, 'rb') as image:
                await ctx.send(file=discord.File(image, filename=file))
            await asyncio.sleep(5)  # Delay of 5 seconds between images

def setup(bot):
    bot.add_cog(ImageSenderCog(bot))
