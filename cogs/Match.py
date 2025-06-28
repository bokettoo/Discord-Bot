import nextcord
from nextcord.ext import commands
from nextcord import Interaction
import requests
from datetime import datetime, timedelta
import asyncio

def get_matches():
    api = "https://streamed.su/api/matches/football/popular"
    response = requests.get(api)
    
    if response.status_code == 200:
        matches = response.json()
        return matches
    elif response.status_code == 400:
        print(response)
        return None
    else:
        return None

class MatchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}  # Dictionary to store cooldowns for each user

    @nextcord.slash_command(name="matches", description="Get a list of football matches.")
    async def send_matches(self, interaction: Interaction):
        user_id = interaction.user.id
        current_time = datetime.now()

        # Check if the user is on cooldown
        if user_id in self.cooldowns:
            cooldown_expiry = self.cooldowns[user_id]
            if current_time < cooldown_expiry:
                time_remaining = (cooldown_expiry - current_time).seconds
                await interaction.response.send_message(f"Please wait {time_remaining} seconds before using this command again.", ephemeral=True)
                return
        
        # Set the user's cooldown to 10 seconds from now
        self.cooldowns[user_id] = current_time + timedelta(seconds=60)
        matches = get_matches()
        
        if not matches:
            await interaction.response.send_message("Could not retrieve matches.", ephemeral=True)
            return
        
        await interaction.response.defer()  # Defers the response to give time for follow-up messages
        
        for match in matches:
            embed = nextcord.Embed(
                title=match.get("title", "No Title"),
                description=match.get("category", "Unknown Category"),
                color=0x1F8B4C
            )
            
            # Check if the date exists and handle the None case
            if match.get("date") is not None:
                match_date = datetime.fromtimestamp(match["date"] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                embed.add_field(name="Date", value=match_date)
            else:
                embed.add_field(name="Date", value="Date not available")
            
            if match.get("teams"):
                home_team = match["teams"]["home"]["name"] if match["teams"]["home"] else "TBD"
                away_team = match["teams"]["away"]["name"] if match["teams"]["away"] else "TBD"
                embed.add_field(name="Teams", value=f"{home_team} vs {away_team}")
                
            # Validate and add the thumbnail URL
            if match.get("poster") and match["poster"].startswith("http"):
                embed.set_thumbnail(url=match["poster"])

            await interaction.followup.send(embed=embed)
            await asyncio.sleep(2)  # Add a 2-second cooldown between embeds
def setup(bot):
    bot.add_cog(MatchCog(bot))

