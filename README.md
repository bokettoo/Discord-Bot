# Discord Bot Project

A multi-bot Discord application with various features including music playback, server management, weather information, and more.

## Features

- **Multi-Bot Support**: Run multiple bots with different configurations
- **Music System**: Play music from YouTube and other sources
- **Server Management**: Manage server settings and permissions
- **Weather Information**: Get weather data for locations
- **Message Handling**: Respond to mentions and direct messages
- **User Management**: Track and manage server members
- **Custom Commands**: Various utility and fun commands

## Project Structure

```
├── main.py              # Main bot entry point
├── start_bot.py         # Python startup script with checks
├── start_bot.bat        # Windows batch startup script
├── config.py            # Configuration loader
├── config.json          # Bot settings and configuration
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
├── cogs/               # Bot command modules
│   ├── MusicCog.py
│   ├── ServerManagement.py
│   ├── weatherCog.py
│   ├── mentionResponder.py
│   ├── MessageChannel.py
│   ├── MessageUser.py
│   ├── DMHistory.py
│   ├── Match.py
│   ├── KanyeCog.py
│   └── members.py
├── images/             # Image assets
├── download/           # Downloaded files
└── responses.json      # Response templates
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Discord Bot Tokens
- Git (optional)

### 2. Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd Jen
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create environment file**
   Create a `.env` file in the project root with your bot tokens:
   ```env
   BOT_TOKEN_KARA_TENKI=your_kara_tenki_bot_token_here
   BOT_TOKEN_Lilly=your_lilly_bot_token_here
   ```

4. **Configure the bot**
   - Edit `config.json` to customize bot settings
   - Update guild IDs and channel IDs as needed
   - Modify allowed user IDs for restricted commands

### 3. Running the Bot

You have several options to start the bot:

#### Option 1: Using the Python Startup Script (Recommended)
```bash
python start_bot.py
```
This script performs automatic checks for:
- Required Python packages
- Configuration file existence
- Environment variables
- Bot tokens in .env file

#### Option 2: Using the Windows Batch Script
```cmd
start_bot.bat
```
This Windows batch file automatically:
- Checks if Python is installed
- Installs requirements if missing
- Verifies .env file exists
- Starts the bot

#### Option 3: Direct Execution
```bash
python main.py
```
Run the main bot directly (no automatic checks).

The bot will prompt you to select which bot to run:
1. Kara Tenki
2. Lilly

## Configuration

### Environment Variables (.env)

The bot automatically loads environment variables based on the configuration in `config.json`. The environment variable names are defined in the `environment_variables` section:

```json
{
  "environment_variables": {
    "bot_tokens": {
      "Kara Tenki": "BOT_TOKEN_KARA_TENKI",
      "Lilly": "BOT_TOKEN_Lilly"
    }
  }
}
```

This means your `.env` file should contain:
```env
BOT_TOKEN_KARA_TENKI=your_kara_tenki_bot_token_here
BOT_TOKEN_Lilly=your_lilly_bot_token_here
```

### Configuration File (config.json)

The `config.json` file contains all bot settings:

```json
{
  "bot_settings": {
    "command_prefix": "!",
    "default_status": "idle",
    "default_activity": "FEETS"
  },
  "environment_variables": {
    "bot_tokens": {
      "Kara Tenki": "BOT_TOKEN_KARA_TENKI",
      "Lilly": "BOT_TOKEN_Lilly"
    }
  },
  "allowed_guilds_channels": {
    "guild_id": ["channel_id1", "channel_id2"]
  },
  "allowed_users": {
    "primary_user_id": 123456789,
    "allowed_user_ids": [123456789, 987654321]
  }
}
```

### Key Settings

- **command_prefix**: The prefix for bot commands (default: "!")
- **default_status**: Bot's default status (online/idle/dnd/invisible)
- **default_activity**: Bot's default activity message
- **environment_variables**: Maps bot names to environment variable names
- **allowed_guilds_channels**: Maps guild IDs to allowed channel IDs
- **allowed_user_ids**: List of user IDs with special permissions

### Adding New Bots

To add a new bot:

1. **Update config.json** - Add the new bot to the `environment_variables.bot_tokens` section:
   ```json
   "environment_variables": {
     "bot_tokens": {
       "Kara Tenki": "BOT_TOKEN_KARA_TENKI",
       "Lilly": "BOT_TOKEN_Lilly",
       "New Bot": "BOT_TOKEN_NEW_BOT"
     }
   }
   ```

2. **Update .env** - Add the corresponding environment variable:
   ```env
   BOT_TOKEN_NEW_BOT=your_new_bot_token_here
   ```

The bot will automatically detect and load the new bot without any code changes!

## Available Commands

### Music Commands
- `!play <song>` - Play a song from YouTube
- `!pause` - Pause current music
- `!resume` - Resume paused music
- `!stop` - Stop music and clear queue
- `!skip` - Skip current song

### Server Management
- `!kick <user>` - Kick a user from the server
- `!ban <user>` - Ban a user from the server
- `!clear <amount>` - Clear messages from a channel

### Utility Commands
- `!weather <location>` - Get weather information
- `!ping` - Check bot latency
- `!info` - Get server information

## Security Features

- **Token Security**: Bot tokens are stored in environment variables
- **Dynamic Configuration**: Environment variable names are defined in config.json
- **Guild Restrictions**: Commands can be restricted to specific guilds and channels
- **User Permissions**: Certain commands require specific user IDs
- **Mention Restrictions**: Configurable mention restrictions per guild

## Logging

The bot includes comprehensive logging:
- Console output with colored text
- File logging to `bot.log`
- Configurable log levels (INFO, DEBUG, WARNING, ERROR)

## Troubleshooting

### Common Issues

1. **Missing Bot Tokens**
   - Ensure your `.env` file exists and contains valid bot tokens
   - Check that environment variable names match those in `config.json`

2. **Permission Errors**
   - Verify the bot has necessary permissions in your Discord server
   - Check that guild and channel IDs are correct in `config.json`

3. **Cog Loading Errors**
   - Ensure all required dependencies are installed
   - Check that cog files are in the `cogs/` directory
   - Verify Python syntax in cog files

4. **Music Not Playing**
   - Check internet connection
   - Verify YouTube-DL is properly installed
   - Ensure bot has voice channel permissions

### Getting Help

If you encounter issues:
1. Check the `bot.log` file for error details
2. Verify all configuration settings
3. Ensure all dependencies are installed correctly
4. Check Discord bot permissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and personal use. Please respect Discord's Terms of Service and API guidelines.

## Support

For support or questions, please check the troubleshooting section above or create an issue in the repository. 