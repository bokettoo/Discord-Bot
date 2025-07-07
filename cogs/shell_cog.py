import nextcord
from nextcord.ext import commands
import asyncio
import subprocess
import os
import sys
import platform
import logging
import tempfile # For creating temporary files

from config import SHELL_CHANNEL_ID, LOGGING_ENABLED, LOGGING_LEVEL, LOGGING_FORMAT, ALLOWED_USER_ID

logger = logging.getLogger(__name__)
if LOGGING_ENABLED:
    logger.setLevel(LOGGING_LEVEL)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(LOGGING_FORMAT)
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
else:
    logger.addHandler(logging.NullHandler())

# Mapping common file extensions to Discord's markdown language identifiers
SYNTAX_HIGHLIGHTING_MAP = {
    "py": "python",
    "js": "javascript",
    "html": "html",
    "css": "css",
    "json": "json",
    "xml": "xml",
    "md": "markdown",
    "txt": "text",
    "sh": "bash",
    "bash": "bash",
    "zsh": "bash",
    "ps1": "powershell",
    "bat": "batch",
    "yml": "yaml",
    "yaml": "yaml",
    "c": "c",
    "cpp": "cpp",
    "java": "java",
    "go": "go",
    "rs": "rust",
    "rb": "ruby",
    "php": "php",
    "sql": "sql",
    "pl": "perl",
    "rb": "ruby",
    "vue": "vue",
    "jsx": "jsx",
    "tsx": "tsx",
    "ts": "typescript",
}

class ShellCog(commands.Cog):
    def __init__(self, bot: nextcord.Client):
        self.bot = bot
        self.is_windows = sys.platform.startswith('win')
        logger.info(f"Bot running on: {platform.system()} {platform.release()}")
        if self.is_windows:
            logger.info("Detected Windows environment. Executing commands directly.")
        else:
            logger.info("Detected non-Windows environment. Executing commands directly.")

        self.current_working_directories = {}

    async def _run_command(self, command: str, cwd: str) -> tuple[str, str, int]:
        """
        Runs a command with a specified current working directory.
        """
        logger.info(f"Executing command: {command} in CWD: {cwd}")
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd
            )
            stdout, stderr = await process.communicate()
            logger.info(f"Command finished with return code {process.returncode}")
            return stdout.decode(errors='ignore'), stderr.decode(errors='ignore'), process.returncode if process.returncode is not None else 1
        except FileNotFoundError:
            logger.error(f"Error: Command '{command.split()[0]}' not found.")
            return "", f"Error: Command '{command.split()[0]}' not found.", 127
        except Exception as e:
            logger.error(f"An unexpected error occurred during command execution: {e}")
            return "", f"An unexpected error occurred during command execution: {e}", 1

    async def _send_output_as_file(self, ctx: commands.Context, filename: str, content: str, language: str = None, prefix_message: str = None):
        """
        Sends the content as a file attachment, with optional prefix message.
        """
        if prefix_message:
            await ctx.send(prefix_message)

        # Append appropriate file extension for highlighting if possible
        if language and language != "text":
            filename_with_ext = f"{filename}.{language}"
        else:
            filename_with_ext = f"{filename}.txt" # Default to .txt

        try:
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8', suffix=f".{language if language else 'txt'}") as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            logger.info(f"Sending content as file: {temp_file_path} with name {filename_with_ext}")
            file = nextcord.File(temp_file_path, filename=filename_with_ext)
            await ctx.send(f"Output too long for message, sending as file `{filename_with_ext}`.", file=file)
            os.remove(temp_file_path) # Clean up the temporary file
            logger.info(f"Temporary file {temp_file_path} removed.")

        except Exception as e:
            logger.error(f"Failed to send output as file: {e}")
            await ctx.send(f":x: An error occurred while trying to send the output as a file: {e}")


    async def _send_long_message(self, ctx: commands.Context, content: str, language: str = None, prefix_message: str = None, send_as_file_threshold: int = 4000):
        """
        Splits a long string into multiple messages, applying syntax highlighting.
        If content is extremely long, it will send it as a file instead.
        """
        # Immediately send as file if content is above a certain threshold
        # This prevents repeatedly hitting the splitting logic for massive outputs
        if len(content) > send_as_file_threshold:
            logger.info(f"Content length {len(content)} exceeds file threshold {send_as_file_threshold}. Sending as file.")
            # Determine a suitable filename
            filename_base = "command_output"
            if prefix_message and "Displaying content of `" in prefix_message:
                # Try to extract original filename from prefix for file download name
                try:
                    filename_base = prefix_message.split('`')[1]
                    if '.' in filename_base:
                        filename_base = os.path.splitext(filename_base)[0] # Remove original extension
                except IndexError:
                    pass # Fallback to default
            
            await self._send_output_as_file(ctx, filename_base, content, language, prefix_message)
            return

        # Send prefix message first, if any
        if prefix_message:
            await ctx.send(prefix_message)
            await asyncio.sleep(0.2) # Small delay before sending content

        if not content:
            await ctx.send("No content to display.")
            return

        lang_str = language if language else ""
        code_block_overhead = 3 + len(lang_str) + 1 + 1 + 3 # ```lang\n + content + \n```
        MAX_CODE_BLOCK_CONTENT_LENGTH = 1990 - code_block_overhead # Use 1990 for generous buffer

        if MAX_CODE_BLOCK_CONTENT_LENGTH <= 0:
            logger.error(f"Calculated MAX_CODE_BLOCK_CONTENT_LENGTH is too small or negative. Language string: '{lang_str}'")
            await ctx.send(":x: Error: Language string too long for code block formatting.")
            return

        # Split content into fixed-size chunks
        chunks = [content[i:i + MAX_CODE_BLOCK_CONTENT_LENGTH] for i in range(0, len(content), MAX_CODE_BLOCK_CONTENT_LENGTH)]

        total_chunks = len(chunks)
        try:
            for i, chunk in enumerate(chunks):
                part_info = f"(Part {i+1}/{total_chunks})" if total_chunks > 1 else ""
                message_part = f"```{lang_str}\n{chunk}```"
                
                final_discord_message = f"{part_info}\n{message_part}" if part_info else message_part

                if len(final_discord_message) > 2000:
                    logger.error(f"FATAL: Message part still exceeds 2000 characters after splitting! Length: {len(final_discord_message)}")
                    # Fallback to file if this still somehow happens
                    await ctx.send(":x: An internal error occurred trying to send message part. Attempting to send as file.")
                    # Recursively call to send as file, but ensure it doesn't get stuck in a loop
                    await self._send_output_as_file(ctx, "error_output", content, language, "Error output was too long:")
                    return # Exit after attempting file send

                await ctx.send(final_discord_message)
                await asyncio.sleep(0.5)

        except nextcord.errors.HTTPException as e:
            if e.code == 50035: # Invalid Form Body, Must be 2000 or fewer in length
                logger.warning(f"Caught HTTP 50035 error during message splitting. Content too large/complex for direct sending. Error: {e}")
                await ctx.send(":x: Output too large/complex for direct message. Attempting to send as file.")
                # Fallback to sending as file
                await self._send_output_as_file(ctx, "command_output", content, language, prefix_message)
            else:
                logger.error(f"An unexpected Discord HTTP error occurred: {e}")
                await ctx.send(f":x: An unexpected Discord error occurred: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during message sending: {e}")
            await ctx.send(f":x: An unexpected error occurred: {e}")

    @commands.command(name="shell", aliases=["sh", "exec", "cmd", "ps"])
    async def shell_command(self, ctx: commands.Context, *, command: str):
        logger.info(f"Command received: {command}")
        logger.info(f"Command Channel ID: {ctx.channel.id}")
        logger.info(f"Configured Shell Channel ID: {SHELL_CHANNEL_ID}")
        logger.info(f"Are IDs equal? {ctx.channel.id == SHELL_CHANNEL_ID}")

        if ctx.channel.id != SHELL_CHANNEL_ID:
            await ctx.send(f"This command can only be used in the designated shell channel (<#{SHELL_CHANNEL_ID}>).")
            logger.warning(f"Command attempted in unauthorized channel: {ctx.channel.id}")
            return

        if not ctx.author.id == ALLOWED_USER_ID:
            await ctx.send("You are not authorized to use this command.")
            logger.warning(f"Unauthorized user {ctx.author.id} attempted to use shell command.")
            return

        channel_id_str = str(ctx.channel.id)
        current_cwd = self.current_working_directories.get(channel_id_str, os.getcwd())

        # --- Handle 'cd' commands specifically ---
        if command.lower().startswith("cd "):
            target_dir = command[3:].strip()
            new_path = os.path.normpath(os.path.join(current_cwd, target_dir))

            if os.path.isdir(new_path):
                self.current_working_directories[channel_id_str] = new_path
                await ctx.send(f"Changed directory to: `{new_path}`")
                logger.info(f"CD command executed. New CWD for channel {channel_id_str}: {new_path}")
                return
            else:
                await ctx.send(f":x: Error: Directory not found or is not a directory: `{new_path}`")
                logger.warning(f"CD command failed. Invalid directory: {new_path}")
                return

        # --- Handle 'cat' or 'type' commands for file viewing ---
        command_parts = command.split(maxsplit=1)
        is_cat_command = False
        file_path_to_view = None
        
        if len(command_parts) > 1:
            cmd_verb = command_parts[0].lower()
            if cmd_verb == "cat" or (self.is_windows and cmd_verb == "type"):
                is_cat_command = True
                file_path_to_view = os.path.normpath(os.path.join(current_cwd, command_parts[1].strip()))

        if is_cat_command and file_path_to_view:
            logger.info(f"Attempting to read file: {file_path_to_view}")
            try:
                if not os.path.exists(file_path_to_view):
                    await ctx.send(f":x: Error: File not found: `{file_path_to_view}`")
                    logger.warning(f"File not found for cat command: {file_path_to_view}")
                    return
                if not os.path.isfile(file_path_to_view):
                    await ctx.send(f":x: Error: Path is not a file: `{file_path_to_view}`")
                    logger.warning(f"Path is not a file for cat command: {file_path_to_view}")
                    return

                with open(file_path_to_view, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                file_extension = os.path.splitext(file_path_to_view)[1].lstrip('.').lower()
                language = SYNTAX_HIGHLIGHTING_MAP.get(file_extension, "text")

                prefix_msg = f"Displaying content of `{os.path.basename(file_path_to_view)}` (detected as `{language}`):"
                await self._send_long_message(ctx, content, language, prefix_message=prefix_msg)
                return

            except IOError as e:
                await ctx.send(f":x: Error reading file `{file_path_to_view}`: {e}")
                logger.error(f"IOError reading file {file_path_to_view}: {e}")
                return
            except Exception as e:
                await ctx.send(f":x: An unexpected error occurred while viewing file: {e}")
                logger.error(f"Unexpected error viewing file {file_path_to_view}: {e}")
                return

        # --- Execute general shell commands ---
        initial_cmd_msg = f"Executing `{command}` in `{current_cwd}` on the bot's host ({'Windows' if self.is_windows else 'Linux'})..."
        await ctx.send(initial_cmd_msg) # This message is always sent directly

        stdout, stderr, returncode = await self._run_command(command, current_cwd)

        combined_output = []
        if stdout:
            combined_output.append(f"STDOUT:\n{stdout}")
        if stderr:
            combined_output.append(f"STDERR (Exit Code: {returncode}):\n{stderr}")
        
        if not stdout and not stderr and returncode == 0:
            combined_output.append("Command executed successfully, no output.")
        elif not stdout and not stderr and returncode != 0:
            combined_output.append(f"Command failed with exit code {returncode}, no output or stderr captured.")

        full_output_text = "\n".join(combined_output)
        
        # Pass a prefix if there's any actual output, otherwise no prefix
        output_prefix = "Command Output:" if full_output_text else None
        await self._send_long_message(ctx, full_output_text, 'text', prefix_message=output_prefix)


    @commands.command(name="resetsh")
    async def reset_shell_state(self, ctx: commands.Context):
        """
        Resets the current working directory for the shell session in this channel.
        """
        if ctx.channel.id != SHELL_CHANNEL_ID:
            await ctx.send(f"This command can only be used in the designated shell channel (<#{SHELL_CHANNEL_ID}>).")
            return
        if not ctx.author.id == ALLOWED_USER_ID:
            await ctx.send("You are not authorized to use this command.")
            return

        channel_id_str = str(ctx.channel.id)
        if channel_id_str in self.current_working_directories:
            del self.current_working_directories[channel_id_str]
            await ctx.send("Shell session state (current directory) has been reset.")
            logger.info(f"Shell state for channel {channel_id_str} reset.")
        else:
            await ctx.send("No active shell session state to reset for this channel.")

def setup(bot):
    bot.add_cog(ShellCog(bot))