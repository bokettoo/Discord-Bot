import nextcord
from nextcord.ext import commands
import os
import sys
import time
import logging
import random
import asyncio
from datetime import datetime
from config import BOT_TOKENS, COMMAND_PREFIX, DEFAULT_STATUS, DEFAULT_ACTIVITY, LOADING_BAR_DURATION, LOADING_BAR_LENGTH, COGS_DIRECTORY, LOGGING_ENABLED, LOGGING_LEVEL, LOGGING_FORMAT

# Enhanced CLI libraries
from pyfiglet import figlet_format
from termcolor import colored
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich.columns import Columns
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.traceback import install
from colorama import init, Fore, Back, Style
import tqdm

# Initialize colorama for cross-platform colors
init(autoreset=True)

# Install rich traceback handler
install()

# Create rich console
console = Console()

# Set up logging
if LOGGING_ENABLED:
    logging.basicConfig(
        level=getattr(logging, LOGGING_LEVEL),
        format=LOGGING_FORMAT,
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)

class HackerCLI:
    def __init__(self):
        self.console = console
        self.start_time = datetime.now()
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def matrix_effect(self, text, delay=0.03):
        """Create a matrix-style typing effect"""
        for char in text:
            self.console.print(char, style="bold green", end="")
            time.sleep(delay)
        self.console.print()
    
    def hacker_banner(self):
        """Display the main hacker-style banner"""
        self.clear_screen()
        
        # ASCII art banner
        banner_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  ██████╗  ██████╗ ██╗  ██╗███████╗████████╗████████╗ ██████╗                 ║
║  ██╔══██╗██╔═══██╗██║ ██╔╝██╔════╝╚══██╔══╝╚══██╔══╝██╔═══██╗                ║
║  ██████╔╝██║   ██║█████╔╝ █████╗     ██║      ██║   ██║   ██║                ║
║  ██╔══██╗██║   ██║██╔═██╗ ██╔══╝     ██║      ██║   ██║   ██║                ║
║  ██████╔╝╚██████╔╝██║  ██╗███████╗   ██║      ██║   ╚██████╔╝                ║
║  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝   ╚═╝      ╚═╝    ╚═════╝                 ║
║                                                                              ║
║                    [bold red]DISCORD BOT CONTROL CENTER[/bold red]           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        
        self.console.print(Panel(banner_text, style="bold blue"))
        
        # System info
        system_info = f"""
[bold cyan]SYSTEM STATUS:[/bold cyan] [green]ONLINE[/green]
[bold cyan]INITIALIZATION TIME:[/bold cyan] {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
[bold cyan]PYTHON VERSION:[/bold cyan] {sys.version.split()[0]}
[bold cyan]PLATFORM:[/bold cyan] {sys.platform}
        """
        
        self.console.print(Panel(system_info, title="[bold red]SYSTEM INFO[/bold red]", style="cyan"))
    
    def loading_sequence(self, message="Initializing system", duration=3):
        """Animated loading sequence with progress bar"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task(message, total=100)
            
            for i in range(100):
                progress.update(task, advance=1)
                time.sleep(duration / 100)
    
    def matrix_loading(self, text, duration=2):
        """Matrix-style loading animation"""
        chars = "01"
        for _ in range(int(duration * 20)):
            matrix_line = "".join(random.choice(chars) for _ in range(50))
            self.console.print(f"[green]{matrix_line}[/green]", end="\r")
            time.sleep(0.05)
        self.console.print()
        self.matrix_effect(text, delay=0.02)
    
    def display_bot_selection(self, bot_names):
        """Display bot selection with enhanced styling"""
        self.console.print("\n[bold yellow]╔══════════════════════════════════════════════════════════════════════════════╗[/bold yellow]")
        self.console.print("[bold yellow]║[/bold yellow] [bold red]AVAILABLE BOT INSTANCES[/bold red] [bold yellow]     ║[/bold yellow]")
        self.console.print("[bold yellow]╚══════════════════════════════════════════════════════════════════════════════╝[/bold yellow]")
        
        table = Table(show_header=True, header_style="bold magenta", border_style="blue")
        table.add_column("ID", style="cyan", justify="center")
        table.add_column("Bot Name", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Token Status", style="red")
        
        for index, bot_name in enumerate(bot_names, start=1):
            token = BOT_TOKENS.get(bot_name, "")
            status = "🟢 READY" if token else "🔴 OFFLINE"
            token_status = "✓ VALID" if token else "✗ MISSING"
            
            table.add_row(
                str(index),
                bot_name,
                status,
                token_status
            )
        
        self.console.print(table)
    
    def get_bot_selection(self, bot_names):
        """Get user bot selection with validation"""
        while True:
            try:
                selection = Prompt.ask(
                    "\n[bold cyan]SELECT BOT INSTANCE[/bold cyan]",
                    choices=[str(i) for i in range(1, len(bot_names) + 1)],
                    default="1"
                )
                return int(selection)
            except KeyboardInterrupt:
                self.console.print("\n[bold red]Operation cancelled by user[/bold red]")
                sys.exit(0)
    
    def display_bot_startup(self, bot_name):
        """Display bot startup sequence"""
        self.console.print(f"\n[bold blue]╔══════════════════════════════════════════════════════════════════════════════╗[/bold blue]")
        self.console.print(f"[bold blue]║[/bold blue] [bold green]INITIALIZING: {bot_name.upper()}[/bold green] [bold blue]║[/bold blue]")
        self.console.print(f"[bold blue]╚══════════════════════════════════════════════════════════════════════════════╝[/bold blue]")
        
        # Matrix effect for bot name
        self.matrix_loading(f"Loading {bot_name}...", 1.5)
        
        # Startup sequence
        startup_steps = [
            "Validating bot credentials...",
            "Establishing Discord connection...",
            "Loading command modules...",
            "Initializing voice systems...",
            "Setting up event handlers...",
            "Configuring bot presence...",
            "Starting bot instance..."
        ]
        
        for step in startup_steps:
            self.loading_sequence(step, 0.8)
    
    def display_guild_info(self, guilds):
        """Display guild information in a styled table"""
        if not guilds:
            self.console.print("[yellow]No guilds connected[/yellow]")
            return
        
        self.console.print(f"\n[bold green]╔══════════════════════════════════════════════════════════════════════════════╗[/bold green]")
        self.console.print("[bold green]║[/bold green] [bold white]CONNECTED GUILDS[/bold white] [bold green]║[/bold green]")
        self.console.print("[bold green]╚══════════════════════════════════════════════════════════════════════════════╝[/bold green]")
        
        table = Table(show_header=True, header_style="bold magenta", border_style="green")
        table.add_column("Guild Name", style="cyan")
        table.add_column("Guild ID", style="yellow")
        table.add_column("Member Count", style="green")
        table.add_column("Bot Permissions", style="red")
        
        for guild in guilds:
            permissions = []
            if guild.me.guild_permissions.administrator:
                permissions.append("ADMIN")
            if guild.me.guild_permissions.manage_channels:
                permissions.append("MANAGE_CHANNELS")
            if guild.me.guild_permissions.manage_messages:
                permissions.append("MANAGE_MESSAGES")
            
            perm_text = ", ".join(permissions) if permissions else "BASIC"
            
            table.add_row(
                guild.name,
                str(guild.id),
                str(guild.member_count),
                perm_text
            )
        
        self.console.print(table)
    
    def display_cog_loading(self, cogs_dir):
        """Display cog loading with progress"""
        if not os.path.exists(cogs_dir):
            self.console.print(f"[red]Cogs directory {cogs_dir} not found![/red]")
            return []
        
        initial_extensions = [f"cogs.{filename[:-3]}" for filename in os.listdir(cogs_dir) 
                            if filename.endswith(".py") and filename != "__init__.py"]
        
        if not initial_extensions:
            self.console.print("[yellow]No cogs found to load[/yellow]")
            return []
        
        self.console.print(f"\n[bold blue]╔══════════════════════════════════════════════════════════════════════════════╗[/bold blue]")
        self.console.print("[bold blue]║[/bold blue] [bold white]LOADING COMMAND MODULES[/bold white] [bold blue]║[/bold blue]")
        self.console.print("[bold blue]╚══════════════════════════════════════════════════════════════════════════════╝[/bold blue]")
        
        loaded_cogs = []
        failed_cogs = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            task = progress.add_task("Loading cogs...", total=len(initial_extensions))
            
            for extension in initial_extensions:
                progress.update(task, description=f"Loading {extension}...")
                try:
                    client.load_extension(extension)
                    loaded_cogs.append(extension)
                    progress.advance(task)
                    time.sleep(0.3)
                except Exception as e:
                    failed_cogs.append((extension, str(e)))
                    progress.advance(task)
                    time.sleep(0.3)
        
        # Display results
        if loaded_cogs:
            self.console.print(f"\n[green]✓ Successfully loaded {len(loaded_cogs)} cogs[/green]")
            for cog in loaded_cogs:
                self.console.print(f"  [green]•[/green] {cog}")
        
        if failed_cogs:
            self.console.print(f"\n[red]✗ Failed to load {len(failed_cogs)} cogs[/red]")
            for cog, error in failed_cogs:
                self.console.print(f"  [red]•[/red] {cog}: {error}")
        
        return loaded_cogs

# Utility function for loading bar (keeping for compatibility)
def loading_bar(duration=LOADING_BAR_DURATION, bar_length=LOADING_BAR_LENGTH):
    for i in range(bar_length + 1):
        percent = (i / bar_length) * 100
        bar = "#" * i + "-" * (bar_length - i)
        sys.stdout.write(f"\r[{bar}] {percent:.1f}%")
        sys.stdout.flush()
        time.sleep(duration / bar_length)
    print()

# Set up bot intents
intents = nextcord.Intents.all()
intents.members = True
intents.message_content = True 

client = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@client.event
async def on_ready():
    cli = HackerCLI()
    
    # Display bot ready message
    cli.console.print(f"\n[bold green]╔══════════════════════════════════════════════════════════════════════════════╗[/bold green]")
    cli.console.print(f"[bold green]║[/bold green] [bold white]BOT STATUS: ONLINE[/bold white] [bold green]║[/bold green]")
    cli.console.print(f"[bold green]╚══════════════════════════════════════════════════════════════════════════════╝[/bold green]")
    
    cli.console.print(f"[bold cyan]Bot logged in as:[/bold cyan] [green]{client.user}[/green] [yellow]({client.user.id})[/yellow]")
    
    if LOGGING_ENABLED:
        logger.info(f"Bot logged in as {client.user} ({client.user.id})")
    
    time.sleep(1)
    
    # Display guild information
    cli.display_guild_info(client.guilds)
    
    # Create invites for guilds
    for guild in client.guilds:
        time.sleep(0.5)
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).create_instant_invite:
                try:
                    invite = await channel.create_invite(max_uses=1, max_age=86400, unique=True)
                    cli.console.print(f"[yellow]Invite for {guild.name}:[/yellow] [cyan]{invite.url}[/cyan]")
                    time.sleep(0.5)
                except Exception as e:
                    cli.console.print(f"[red]Could not create invite for {guild.name}: {e}[/red]")
                    if LOGGING_ENABLED:
                        logger.error(f"Could not create invite for {guild.name}: {e}")
                    time.sleep(0.5)
                break

    # Set bot status and activity
    status_map = {
        "online": nextcord.Status.online,
        "idle": nextcord.Status.idle,
        "dnd": nextcord.Status.dnd,
        "invisible": nextcord.Status.invisible
    }
    
    status = status_map.get(DEFAULT_STATUS, nextcord.Status.idle)
    await client.change_presence(activity=nextcord.Game(name=DEFAULT_ACTIVITY), status=status)
    
    cli.console.print(f"\n[bold green]Bot is now ready and listening for commands![/bold green]")

def validate_tokens():
    """Validate that all required bot tokens are present in environment variables"""
    missing_tokens = []
    for bot_name, token in BOT_TOKENS.items():
        if not token:
            missing_tokens.append(bot_name)
    
    if missing_tokens:
        console.print(f"[red]Missing bot tokens for: {', '.join(missing_tokens)}[/red]")
        console.print("[yellow]Please check your .env file and ensure all required tokens are set.[/yellow]")
        if LOGGING_ENABLED:
            logger.error(f"Missing bot tokens for: {', '.join(missing_tokens)}")
        return False
    return True

if __name__ == "__main__":
    cli = HackerCLI()
    
    try:
        # Display hacker banner
        cli.hacker_banner()
        
        # Validate tokens first
        if not validate_tokens():
            sys.exit(1)
        
        bot_names = list(BOT_TOKENS.keys())

        if not bot_names:
            console.print("[red]No bots found in the configuration.[/red]")
            if LOGGING_ENABLED:
                logger.error("No bots found in the configuration.")
            sys.exit(1)

        # Display bot selection
        cli.display_bot_selection(bot_names)
        
        # Get user selection
        selection = cli.get_bot_selection(bot_names)
        selected_bot_name = bot_names[selection - 1]
        
        # Display bot startup sequence
        cli.display_bot_startup(selected_bot_name)
        
        # Load cogs
        loaded_cogs = cli.display_cog_loading(COGS_DIRECTORY)
        
        if LOGGING_ENABLED:
            logger.info(f"Starting bot: {selected_bot_name}")
        
        # Start the bot
        token = BOT_TOKENS[selected_bot_name]
        client.run(token)
        
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Bot shutdown requested by user[/bold yellow]")
        if LOGGING_ENABLED:
            logger.info("Bot shutdown requested by user")
    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")
        if LOGGING_ENABLED:
            logger.error(f"An error occurred: {e}")
        sys.exit(1)
