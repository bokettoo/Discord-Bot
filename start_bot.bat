@echo off
echo Discord Bot Startup
echo ===================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking requirements...
python -c "import nextcord, dotenv, pyfiglet, termcolor" >nul 2>&1
if errorlevel 1 (
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install requirements
        pause
        exit /b 1
    )
)

REM Check if .env file exists
if not exist ".env" (
    echo Error: .env file not found
    echo Please create a .env file with your bot tokens:
    echo BOT_TOKEN_KARA_TENKI=your_token_here
    echo BOT_TOKEN_Lilly=your_token_here
    pause
    exit /b 1
)

echo Starting bot...
python main.py

pause 