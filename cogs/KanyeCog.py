import nextcord
from nextcord.ext import commands
import aiohttp

class KanyeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="kanye", description="Get a random Kanye West quote.")
    async def kanye(self, interaction: nextcord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.kanye.rest') as response:
                if response.status == 200:
                    data = await response.json()
                    quote = data.get("quote")
                    if quote:
                        await interaction.response.send_message(f"Kanye says: \"{quote}\"")
                    else:
                        await interaction.response.send_message("Couldn't fetch a quote, please try again later.")
                else:
                    await interaction.response.send_message("Failed to reach the Kanye Rest API, please try again later.")

# Setup the cog
def setup(bot):
    bot.add_cog(KanyeCog(bot))
