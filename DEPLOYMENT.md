# Deployment Guide - Dopium Bot

This guide explains how to run the Dopium Telegram bot in production.

## Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)
- Server with SSH access (for remote deployment)
- Systemd (for Linux) or alternative process manager

## Quick Start

### Option 1: Simple Background Process (Quick & Easy)

1. **Make scripts executable:**
   ```bash
   chmod +x run.sh run_background.sh stop.sh
   ```

2. **Start the bot in background:**
   ```bash
   ./run_background.sh
   ```

3. **Check if it's running:**
   ```bash
   tail -f logs/bot.log
   ```

4. **Stop the bot:**
   ```bash
   ./stop.sh
   ```

### Option 2: Using systemd (Recommended for Production)

1. **Edit the service file:**
   ```bash
   nano dopium-bot.service
   ```
   
   Update these paths:
   - `User=YOUR_USERNAME` → Your Linux username
   - `WorkingDirectory=/path/to/Dopium` → Full path to your project
   - `ExecStart=/path/to/Dopium/venv/bin/python` → Full path to Python in venv
   - All `/path/to/Dopium` → Replace with actual path

2. **Copy service file to systemd:**
   ```bash
   sudo cp dopium-bot.service /etc/systemd/system/
   ```

3. **Reload systemd:**
   ```bash
   sudo systemctl daemon-reload
   ```

4. **Enable service (start on boot):**
   ```bash
   sudo systemctl enable dopium-bot
   ```

5. **Start the service:**
   ```bash
   sudo systemctl start dopium-bot
   ```

6. **Check status:**
   ```bash
   sudo systemctl status dopium-bot
   ```

7. **View logs:**
   ```bash
   sudo journalctl -u dopium-bot -f
   ```

8. **Stop the service:**
   ```bash
   sudo systemctl stop dopium-bot
   ```

9. **Restart the service:**
   ```bash
   sudo systemctl restart dopium-bot
   ```

### Option 3: Using screen (Simple Alternative)

1. **Install screen (if not installed):**
   ```bash
   sudo apt-get install screen  # Debian/Ubuntu
   # or
   brew install screen  # macOS
   ```

2. **Start a new screen session:**
   ```bash
   screen -S dopium-bot
   ```

3. **Run the bot:**
   ```bash
   ./run.sh
   ```

4. **Detach from screen:**
   - Press `Ctrl+A` then `D`

5. **Reattach to screen:**
   ```bash
   screen -r dopium-bot
   ```

6. **List all screen sessions:**
   ```bash
   screen -ls
   ```

### Option 4: Using tmux (Alternative to screen)

1. **Install tmux:**
   ```bash
   sudo apt-get install tmux  # Debian/Ubuntu
   # or
   brew install tmux  # macOS
   ```

2. **Start a new tmux session:**
   ```bash
   tmux new -s dopium-bot
   ```

3. **Run the bot:**
   ```bash
   ./run.sh
   ```

4. **Detach from tmux:**
   - Press `Ctrl+B` then `D`

5. **Reattach to tmux:**
   ```bash
   tmux attach -t dopium-bot
   ```

## Environment Setup

1. **Create `.env` file:**
   ```bash
   cp .env.example .env  # If you have an example file
   # or create manually
   nano .env
   ```

2. **Add required variables:**
   ```env
   BOT_TOKEN=your_bot_token_here
   GROUP_ID=your_group_id_here
   CHANNEL_ID=your_channel_id_here
   CHANNEL_USERNAME=your_channel_username_here
   ```

3. **Set proper permissions:**
   ```bash
   chmod 600 .env  # Only owner can read/write
   ```

## Directory Structure

After setup, your project should look like:
```
Dopium/
├── main.py
├── run.sh
├── run_background.sh
├── stop.sh
├── .env
├── logs/
│   ├── bot.log
│   └── bot.error.log
├── data/
│   └── dopium.db
└── venv/
```

## Logging

- **Background script logs:** `logs/bot.log`
- **Systemd logs:** `sudo journalctl -u dopium-bot -f`
- **Screen/tmux:** View directly in the session

## Monitoring

### Check if bot is running:

**For background script:**
```bash
ps aux | grep "python main.py"
# or
cat bot.pid
```

**For systemd:**
```bash
sudo systemctl status dopium-bot
```

**For screen:**
```bash
screen -ls
```

## Troubleshooting

### Bot not starting?

1. **Check Python version:**
   ```bash
   python --version  # Should be 3.8+
   ```

2. **Check virtual environment:**
   ```bash
   source venv/bin/activate
   pip list
   ```

3. **Check .env file:**
   ```bash
   cat .env  # Make sure BOT_TOKEN is set
   ```

4. **Check logs:**
   ```bash
   tail -n 50 logs/bot.log
   ```

### Bot keeps crashing?

1. **Check systemd logs:**
   ```bash
   sudo journalctl -u dopium-bot -n 100
   ```

2. **Check for conflicts:**
   ```bash
   ps aux | grep "python main.py"
   # Kill any duplicate processes
   ```

3. **Verify database permissions:**
   ```bash
   ls -la data/dopium.db
   ```

## Updating the Bot

1. **Stop the bot:**
   ```bash
   ./stop.sh  # or sudo systemctl stop dopium-bot
   ```

2. **Pull latest changes:**
   ```bash
   git pull  # if using git
   ```

3. **Update dependencies (if needed):**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt --upgrade
   ```

4. **Start the bot:**
   ```bash
   ./run_background.sh  # or sudo systemctl start dopium-bot
   ```

## Backup

### Database Backup

```bash
# Create backup
cp data/dopium.db data/dopium.db.backup.$(date +%Y%m%d_%H%M%S)

# Or automated backup script
#!/bin/bash
BACKUP_DIR="/path/to/backups"
mkdir -p $BACKUP_DIR
cp data/dopium.db $BACKUP_DIR/dopium.db.$(date +%Y%m%d_%H%M%S)
```

## Security Best Practices

1. **Never commit `.env` file to git**
2. **Use strong permissions on `.env`:** `chmod 600 .env`
3. **Keep dependencies updated:** `pip install --upgrade -r requirements.txt`
4. **Regular backups of database**
5. **Monitor logs for suspicious activity**

## Recommended Setup for Production

For a production server, we recommend:

1. **Use systemd** (Option 2) - Automatic restart, better logging
2. **Set up log rotation** to prevent disk space issues
3. **Regular database backups**
4. **Monitor bot status** with a simple health check script
5. **Use a reverse proxy** if exposing any web interface

## Need Help?

- Check logs first: `tail -f logs/bot.log`
- Verify environment variables are set correctly
- Ensure Python version is 3.8+
- Make sure all dependencies are installed

