#!/usr/bin/env python3
"""
Discord Bot Configuration Setup
Interactive script to help configure the bot settings.
"""

import json
import os
from pathlib import Path

def load_config():
    """Load configuration from config.json or return default"""
    config_file = Path("config.json")
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    else:
        # Return default config structure
        return {
            "environment_variables": {
                "bot_tokens": {
                    "Kara Tenki": "BOT_TOKEN_KARA_TENKI",
                    "Lilly": "BOT_TOKEN_Lilly"
                }
            }
        }

def create_env_file():
    """Create .env file with bot tokens"""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✓ .env file already exists")
        return True
    
    # Load config to get environment variable names
    config = load_config()
    env_vars = config.get("environment_variables", {}).get("bot_tokens", {})
    
    print("\n=== Bot Token Setup ===")
    print("You need to provide your Discord bot tokens.")
    print("Get your bot tokens from: https://discord.com/developers/applications")
    
    env_content = "# Discord Bot Tokens\n"
    tokens_provided = True
    
    for bot_name, env_var_name in env_vars.items():
        token = input(f"Enter {bot_name} bot token ({env_var_name}): ").strip()
        if not token:
            print(f"✗ Token for {bot_name} is required!")
            tokens_provided = False
            break
        env_content += f"{env_var_name}={token}\n"
    
    if not tokens_provided:
        return False
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✓ .env file created successfully")
    return True

def create_config_json():
    """Create config.json with default settings"""
    config_file = Path("config.json")
    
    if config_file.exists():
        print("✓ config.json already exists")
        return True
    
    default_config = {
        "bot_settings": {
            "command_prefix": "!",
            "default_status": "idle",
            "default_activity": "FEETS",
            "loading_bar_duration": 2,
            "loading_bar_length": 20
        },
        "environment_variables": {
            "bot_tokens": {
                "Kara Tenki": "BOT_TOKEN_KARA_TENKI",
                "Lilly": "BOT_TOKEN_Lilly"
            }
        },
        "allowed_guilds_channels": {
            "1260253270627319868": ["1277999262667640946"],
            "1244424002571599882": ["1279151335828226179"]
        },
        "guild_restricted_mentions": {
            "1260253270627319868": ["@everyone", "@here"]
        },
        "allowed_users": {
            "primary_user_id": 595391505208967168,
            "allowed_user_ids": [
                595391505208967168,
                974800514661363712,
                1203784697130385472,
                1224111094180876433,
                643450887523532806,
                470880906937106432,
                708047987510607992
            ]
        },
        "cogs": {
            "auto_load": True,
            "cogs_directory": "./cogs"
        },
        "logging": {
            "enabled": True,
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }
    
    print("\n=== Configuration Setup ===")
    print("Setting up default configuration...")
    
    # Allow user to customize some settings
    prefix = input("Command prefix (default: !): ").strip() or "!"
    activity = input("Default activity message (default: FEETS): ").strip() or "FEETS"
    
    default_config["bot_settings"]["command_prefix"] = prefix
    default_config["bot_settings"]["default_activity"] = activity
    
    with open(config_file, 'w') as f:
        json.dump(default_config, f, indent=2)
    
    print("✓ config.json created successfully")
    print("Note: You may need to update guild IDs and channel IDs in config.json")
    return True

def main():
    print("Discord Bot Configuration Setup")
    print("=" * 40)
    
    # Create config.json first (needed for env var names)
    if not create_config_json():
        print("Failed to create config.json")
        return
    
    # Create .env file
    if not create_env_file():
        print("Failed to create .env file")
        return
    
    print("\n=== Setup Complete ===")
    print("✓ .env file created with bot tokens")
    print("✓ config.json created with default settings")
    print("\nNext steps:")
    print("1. Update guild IDs and channel IDs in config.json if needed")
    print("2. Install requirements: pip install -r requirements.txt")
    print("3. Run the bot: python main.py")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main() 