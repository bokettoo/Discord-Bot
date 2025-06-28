import nextcord
from nextcord.ext import commands
from nextcord import Permissions
from nextcord.abc import GuildChannel
import requests
import asyncio
from bs4 import BeautifulSoup
from config import ALLOWED_USER_ID

class Playboy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def scrape_links(self, url: str):
        """Helper function to scrape href links from a given URL."""
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            return None, f"Failed to fetch the URL: {e}"

        soup = BeautifulSoup(response.text, 'html.parser')
        main = soup.find('main')
        if not main:
            return None, "No <main> element found in the HTML."

        ul = main.find('ul')
        if not ul:
            return None, "No <ul> element found inside <main>."
        
        list_items = ul.find_all('li')
        if not list_items:
            return None, "No <li> element found inside <ul>."

        hrefs = []
        for item in list_items:
            a_tag = item.find('a')  # Find the <a> tag inside the <li>
            if a_tag and 'href' in a_tag.attrs and a_tag['href'] != 'javascript:void(0);':
                hrefs.append(a_tag['href'])

        if not hrefs:
            return None, "No links found in the specified structure."

        return hrefs, None

    @nextcord.slash_command(
        name="playboy",
        description="Scrapes href links from a URL and sends them with a delay.",
        default_member_permissions=Permissions(administrator=True)
    )
    async def playboy(self, interaction: nextcord.Interaction, url: str, channel: GuildChannel):
        if interaction.user.id != ALLOWED_USER_ID:
            await interaction.response.send_message('Boketto galik sir t7wa', ephemeral=True)
            return

        await interaction.response.send_message("Scraping links, please wait...", ephemeral=True)

        async def scrape_and_process(url):
            hrefs, error = await self.scrape_links(url)
            if error:
                await interaction.followup.send(error)
                return []
            return hrefs

        # Initial scrape
        hrefs = await scrape_and_process(url)
        if not hrefs:
            return

        # Process first-level links
        for href in hrefs:
            sub_hrefs = await scrape_and_process(href)
            if not sub_hrefs:
                return

            # Process second-level links
            for sub_href in sub_hrefs:
                await channel.send(sub_href)
                await asyncio.sleep(5)  # Async delay to prevent blocking

# Setup the cog
def setup(bot):
    bot.add_cog(Playboy(bot))
