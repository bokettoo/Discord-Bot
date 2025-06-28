import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SelectOption, Permissions
from nextcord.ui import Select, Button, View
from config import ALLOWED_USER_ID

class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.selected_guild_id = None  # Variable to store the selected guild ID

    @nextcord.slash_command(
        name="manage_servers", 
        description="Manage the servers the bot is in.", 
        default_member_permissions=Permissions(administrator=True)
    )
    async def manage_servers(self, interaction: Interaction):
        """
        Command to manage servers the bot is in.
        """

        # Check if the user is allowed to use this command
        if interaction.user.id != ALLOWED_USER_ID:
            await interaction.response.send_message(
                "You are not authorized to use this command.",
                ephemeral=True
            )
            return

        guilds = self.bot.guilds
        
        # Create a select menu with all the servers
        select_options = [
            SelectOption(label=guild.name, description=str(guild.id), value=str(guild.id))
            for guild in guilds
        ]

        select_menu = Select(
            placeholder="Select a server to leave...",
            options=select_options,
            custom_id="select_server"
        )

        # Create a button to leave the server
        leave_button = Button(label="Leave Server", style=nextcord.ButtonStyle.danger, custom_id="leave_server_button")

        # View to hold the select menu and button
        view = View()
        view.add_item(select_menu)
        view.add_item(leave_button)

        # Create an embed to display the select menu and button
        embed = nextcord.Embed(
            title="Server Management",
            description="Select a server from the dropdown menu and click the 'Leave Server' button to remove the bot from that server.",
            color=nextcord.Color.blue()
        )

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        # Define the callback for when a server is selected
        async def handle_select_menu(select_interaction: Interaction):
            self.selected_guild_id = int(select_menu.values[0])  # Store the selected guild ID
            selected_guild = self.bot.get_guild(self.selected_guild_id)

            if selected_guild:
                await select_interaction.response.send_message(
                    f"Selected server: {selected_guild.name}", ephemeral=True
                )
            else:
                await select_interaction.response.send_message(
                    "The bot is not in the selected server.", ephemeral=True
                )

        # Define the callback for when the leave button is pressed
        async def handle_leave_button(button_interaction: Interaction):
            if self.selected_guild_id:
                selected_guild = self.bot.get_guild(self.selected_guild_id)

                if selected_guild:
                    await selected_guild.leave()
                    await button_interaction.response.send_message(
                        f"Successfully left the server: {selected_guild.name}", ephemeral=True
                    )
                else:
                    await button_interaction.response.send_message(
                        "The bot is not in the selected server.", ephemeral=True
                    )
            else:
                await button_interaction.response.send_message(
                    "Please select a server before attempting to leave.", ephemeral=True
                )

        # Set the callbacks for the interactions
        select_menu.callback = handle_select_menu
        leave_button.callback = handle_leave_button

def setup(bot):
    bot.add_cog(ServerManagement(bot))
