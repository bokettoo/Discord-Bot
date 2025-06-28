import nextcord
from nextcord.ext import commands
from nextcord import Interaction

class members(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="total_members", description="Get the total number of members in all guilds.")
    async def total_members(self, interaction: Interaction):
        total_members = 0
        for guild in self.bot.guilds:
            total_members += guild.member_count

        await interaction.response.send_message(f"The total number of members in all guilds is {total_members}")


def setup(bot):
    bot.add_cog(members(bot))

