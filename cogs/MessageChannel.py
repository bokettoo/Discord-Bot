import nextcord
from nextcord.ext import commands
from nextcord import SlashOption, Permissions
from config import ALLOWED_USER_IDS, ALLOWED_USER_ID, GUILD_RESTRICTED_MENTIONS  # Import the config values

class MessageChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="message_channel",
        description="Send a message to a specified channel",
        default_member_permissions=Permissions(administrator=False)
        )
    async def message_channel(
        self,
        interaction: nextcord.Interaction,
        message: str = SlashOption(
            name="message",
            description="The message to send",
            required=False,
            default=" "
        ),
        channel: nextcord.TextChannel = SlashOption(
            name="channel",
            description="The channel to send the message to",
            required=False,
            default=None
        ),
        image: nextcord.Attachment = SlashOption(
            name="image",
            description="The image to send",
            required=False,
            default=None
        ),
        message_id: str = SlashOption(
            name="message_id",
            description="The ID of the message to reply to",
            required=False,
            default=None
        )
    ):
        guild_id = interaction.guild_id
        
        # Check if the user ID matches the allowed user IDs
        if interaction.user.id not in ALLOWED_USER_IDS:
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return

        # Get the restricted mentions for the guild
        restricted_mentions = GUILD_RESTRICTED_MENTIONS.get(guild_id, [])

        # Check if the message contains any restricted mentions and the user is not the special allowed user
        if any(mention in message for mention in restricted_mentions) and interaction.user.id != ALLOWED_USER_ID:
            await interaction.response.send_message(f"You are not allowed to mention {', '.join(restricted_mentions)} in this guild.", ephemeral=True)
            return

        if channel is None:
            channel = interaction.channel
        
        await interaction.response.defer(ephemeral=True)

        # Prepare the message
        content = message
        files = []

        # If an image is provided, add it to the files list
        if image is not None:
            files.append(await image.to_file())

        # Attempt to fetch the message to reply to
        reply_to_message = None
        if message_id:
            try:
                reply_to_message = await channel.fetch_message(int(message_id))
            except:
                await interaction.followup.send("Could not find the specified message to reply to.", ephemeral=True)
                return

        # Send the message with or without the image, as a reply to the original message if provided
        await channel.send(content=content, files=files, reference=reply_to_message)
        await interaction.followup.send(f"Message has been sent to {channel.mention}", ephemeral=True)

def setup(bot):
    bot.add_cog(MessageChannel(bot))
