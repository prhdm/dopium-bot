#!/bin/bash

# Dopium Bot Startup Script
# This script activates the virtual environment and runs the bot

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your BOT_TOKEN and other settings."
    exit 1
fi

# Run the bot
echo "🚀 Starting Dopium Bot..."
python main.py

