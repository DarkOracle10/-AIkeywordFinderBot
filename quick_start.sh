#!/bin/bash

echo "🔍 AI Keyword Finder Bot - Quick Setup"
echo "======================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create venv
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate
echo "🔧 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "   - Get API credentials from: https://my.telegram.org/apps"
echo "   - Get bot token from: @BotFather on Telegram"
echo "2. Run Telegram bot: python run_bot.py"
echo "3. Run Desktop GUI: python run_gui.py"
echo "4. Run both: python run_both.py"
echo ""
