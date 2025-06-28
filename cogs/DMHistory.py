import nextcord
from nextcord.ext import commands
import datetime
import config

class DMHistory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="dm_history",
        description="Fetch DM messages between the bot and a specified user"
    )
    async def dm_history(
        self, 
        interaction: nextcord.Interaction, 
        user: nextcord.User = nextcord.SlashOption(
            description="The user to fetch DM history with",
            required=True
        ),
        message_limit: int = nextcord.SlashOption(
            description="Number of messages to fetch (default: 10)",
            required=False,
            default=10,
            min_value=1,
            max_value=50
        ),
        private: bool = nextcord.SlashOption(
            description="Whether to show the message only to you (default: True)",
            required=False,
            default=True
        )
    ):
        # Check if the user is authorized
        if interaction.user.id != config.ALLOWED_USER_ID:
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=private)
        
        # Get or create DM channel with the user
        dm_channel = user.dm_channel
        if dm_channel is None:
            dm_channel = await user.create_dm()
        
        # Fetch messages
        try:
            messages = []
            async for message in dm_channel.history(limit=message_limit):
                messages.append(message)
            
            # Reverse the list to show oldest first
            messages.reverse()
            
            # Create formatted text output
            output = f"# 💬 Conversation with {user.name}\n"
            output += f"Last {len(messages)} messages in DM history\n\n"
            
            if not messages:
                output += "**No Messages**\nNo message history found with this user.\n"
            else:
                for i, msg in enumerate(messages, 1):
                    # Create timestamp format
                    timestamp = msg.created_at.strftime("%b %d, %H:%M")
                    
                    # Different styling for bot vs user messages
                    if msg.author.id == self.bot.user.id:
                        output += f"**🤖 Bot • {timestamp}**\n"
                    else:
                        output += f"**👤 {user.name} • {timestamp}**\n"
                    
                    content = msg.content if msg.content else "*[No text content]*"
                    
                    # Add attachments info if any
                    if msg.attachments:
                        content += f"\n*[{len(msg.attachments)} attachment(s)]*"
                    
                    output += f"{content}\n\n"
            
            output += f"*Requested by {interaction.user.name} at {datetime.datetime.now().strftime('%b %d, %H:%M')}*"
            
            await interaction.followup.send(output, ephemeral=private)
            
        except nextcord.Forbidden:
            await interaction.followup.send("I don't have permission to access DM history with this user.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)

def setup(bot):
    bot.add_cog(DMHistory(bot))