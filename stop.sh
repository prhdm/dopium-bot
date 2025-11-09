#!/bin/bash

# Dopium Bot Stop Script

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

if [ -f "bot.pid" ]; then
    PID=$(cat bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "🛑 Stopping bot (PID: $PID)..."
        kill $PID
        rm bot.pid
        echo "✅ Bot stopped successfully"
    else
        echo "⚠️  Bot process not found (PID: $PID)"
        rm bot.pid
    fi
else
    echo "⚠️  bot.pid file not found. Trying to find and kill bot process..."
    pkill -f "python main.py"
    echo "✅ Done"
fi

