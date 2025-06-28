#!/usr/bin/env python3
"""
Discord Bot Startup Script
A simple script to start the Discord bot with various options.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def load_config():
    """Load configuration from config.json"""
    config_file = Path("config.json")
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    return None

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import nextcord
        import dotenv
        import pyfiglet
        import termcolor
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required tokens"""
    env_file = Path(".env")
    if not env_file.exists():
        print("✗ .env file not found")
        print("Please create a .env file with your bot tokens")
        return False
    
    # Load config to get environment variable names
    config = load_config()
    if not config:
        print("✗ config.json not found, cannot verify environment variables")
        return False
    
    env_vars = config.get("environment_variables", {}).get("bot_tokens", {})
    if not env_vars:
        print("✗ No bot tokens configured in config.json")
        return False
    
    # Check if tokens are in .env file
    with open(env_file, 'r') as f:
        content = f.read()
        missing_vars = []
        for bot_name, env_var_name in env_vars.items():
            if env_var_name not in content:
                missing_vars.append(f"{env_var_name} ({bot_name})")
        
        if missing_vars:
            print(f"✗ Missing environment variables in .env file: {', '.join(missing_vars)}")
            return False
    
    print("✓ .env file found with all required bot tokens")
    return True

def check_config():
    """Check if config.json exists"""
    config_file = Path("config.json")
    if not config_file.exists():
        print("✗ config.json not found")
        return False
    
    print("✓ config.json found")
    return True

def main():
    print("Discord Bot Startup Check")
    print("=" * 30)
    
    # Check prerequisites
    if not check_requirements():
        sys.exit(1)
    
    if not check_config():
        sys.exit(1)
    
    if not check_env_file():
        sys.exit(1)
    
    print("\nStarting bot...")
    print("=" * 30)
    
    # Start the main bot
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Bot exited with error code: {e.returncode}")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 