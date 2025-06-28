import nextcord
from nextcord.ext import commands
import requests
from bs4 import BeautifulSoup
from config import ALLOWED_USER_ID

class PlayboyVideoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def scrape_source_tags(self, target_url):
        try:
            response = requests.get(target_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                source_tags = soup.find_all("source")
                return [source.get("src") for source in source_tags if source.get("src")]
            else:
                return f"Failed to fetch {target_url}. Status code: {response.status_code}"
        except Exception as e:
            return f"An error occurred while scraping {target_url}: {e}"

    # Slash command to scrape src from <source> tags
    @nextcord.slash_command(name="playboyVideo", description="Scrape the src from <source> tags on the provided link")
    async def playboy_video(self, interaction: nextcord.Interaction, url: str):
        # Check if the user is allowed to use this command
        if interaction.user.id != ALLOWED_USER_ID:
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return

        # Check if the user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
            return

        # Call the function to scrape the src tags from the URL
        src_links = await self.scrape_source_tags(url)
        
        if isinstance(src_links, list):
            if src_links:
                await interaction.response.send_message("\n".join(src_links))
            else:
                await interaction.response.send_message("No <source> tags with src found on the provided URL.", ephemeral=True)
        else:
            await interaction.response.send_message(src_links, ephemeral=True)

# Setup function to add the cog to the bot
def setup(bot):
    bot.add_cog(PlayboyVideoCog(bot))
