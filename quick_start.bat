@echo off
echo 🔍 AI Keyword Finder Bot - Quick Setup
echo ======================================

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python found
python --version

:: Create venv
echo 📦 Creating virtual environment...
python -m venv venv

:: Activate
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

:: Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

:: Create .env
if not exist .env (
    echo 📝 Creating .env file...
    copy .env.example .env
    echo ⚠️  Please edit .env and add your API keys
)

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file and add your API keys
echo    - Get API credentials from: https://my.telegram.org/apps
echo    - Get bot token from: @BotFather on Telegram
echo 2. Run Telegram bot: python run_bot.py
echo 3. Run Desktop GUI: python run_gui.py
echo 4. Run both: python run_both.py
echo.
pause
