import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load configuration from config.json
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: config.json not found. Using default configuration.")
        return get_default_config()

def get_default_config():
    return {
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
            "enabled": False,
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }

# Load the configuration
config = load_config()

# Dynamically load bot tokens from environment variables based on config.json
def load_bot_tokens():
    """Load bot tokens from environment variables using names from config.json"""
    bot_tokens = {}
    env_vars = config.get("environment_variables", {}).get("bot_tokens", {})
    
    for bot_name, env_var_name in env_vars.items():
        token = os.getenv(env_var_name)
        if token:
            bot_tokens[bot_name] = token
        else:
            print(f"Warning: Environment variable '{env_var_name}' not found for bot '{bot_name}'")
    
    return bot_tokens

# Load bot tokens dynamically
BOT_TOKENS = load_bot_tokens()

# Extract commonly used settings for backward compatibility
ALLOWED_GUILDS_CHANNELS = {int(k): v for k, v in config["allowed_guilds_channels"].items()}
GUILD_RESTRICTED_MENTIONS = {int(k): v for k, v in config["guild_restricted_mentions"].items()}
ALLOWED_USER_ID = config["allowed_users"]["primary_user_id"]
ALLOWED_USER_IDS = config["allowed_users"]["allowed_user_ids"]

# Bot settings
COMMAND_PREFIX = config["bot_settings"]["command_prefix"]
DEFAULT_STATUS = config["bot_settings"]["default_status"]
DEFAULT_ACTIVITY = config["bot_settings"]["default_activity"]
LOADING_BAR_DURATION = config["bot_settings"]["loading_bar_duration"]
LOADING_BAR_LENGTH = config["bot_settings"]["loading_bar_length"]

# Cogs settings
COGS_AUTO_LOAD = config["cogs"]["auto_load"]
COGS_DIRECTORY = config["cogs"]["cogs_directory"]

# Logging settings
LOGGING_ENABLED = config["logging"]["enabled"]
LOGGING_LEVEL = config["logging"]["level"]
LOGGING_FORMAT = config["logging"]["format"] 