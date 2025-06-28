import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
from config import ALLOWED_USER_ID

class MessageUser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="message_user", 
        description="Send a direct message to a user.",
        default_member_permissions=nextcord.Permissions(administrator=True)
    )
    async def message_user(
        self, 
        interaction: nextcord.Interaction, 
        member: nextcord.Member = SlashOption(
            description="User to send the message to", 
            required=True
        ),
        message: str = SlashOption(
            name="message",
            description="The message you want to send",
            required=True
        ),
        attachment: nextcord.Attachment = SlashOption(
            name="attachment",
            description="Optional attachment to include in the message",
            required=False
        )
    ):
        # Check if the user is authorized to use this command
        if interaction.user.id != ALLOWED_USER_ID:
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return

        # Check if the member is not a bot
        if member.bot:
            await interaction.response.send_message("You cannot send a message to a bot.", ephemeral=True)
            return

        # Attempt to send the message with or without attachment
        try:
            if attachment:
                # Download the attachment and send it
                file = await attachment.to_file()
                await member.send(content=message, file=file)
            else:
                # Send only the message if no attachment
                await member.send(message)
                
            await interaction.response.send_message(f"Message sent successfully to {member.name}.", ephemeral=True)
        except nextcord.Forbidden:
            await interaction.response.send_message(f"Failed to send the message to {member.name}. They might have DMs disabled.", ephemeral=True)
        except nextcord.HTTPException as e:
            await interaction.response.send_message(f"Failed to send the message to {member.name} due to an unexpected error: {e}", ephemeral=True)

def setup(bot):
    bot.add_cog(MessageUser(bot))
