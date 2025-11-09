#!/bin/bash

# Dopium Bot Background Startup Script
# This script runs the bot in the background using nohup

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

# Create logs directory if it doesn't exist
mkdir -p logs

# Run the bot in background with nohup
echo "🚀 Starting Dopium Bot in background..."
nohup python main.py > logs/bot.log 2>&1 &

# Save the PID
echo $! > bot.pid

echo "✅ Bot started in background!"
echo "📝 PID: $(cat bot.pid)"
echo "📋 Logs: logs/bot.log"
echo ""
echo "To stop the bot, run: ./stop.sh"
echo "To view logs: tail -f logs/bot.log"

