# Quick Start Guide - Running Dopium Bot

## 🚀 Fastest Way to Run (Background Process)

1. **Make scripts executable:**
   ```bash
   chmod +x run_background.sh stop.sh
   ```

2. **Start the bot:**
   ```bash
   ./run_background.sh
   ```

3. **Check logs:**
   ```bash
   tail -f logs/bot.log
   ```

4. **Stop the bot:**
   ```bash
   ./stop.sh
   ```

That's it! The bot will run in the background even after you close the terminal.

---

## 📋 Other Options

### Option A: Run in Terminal (for testing)
```bash
./run.sh
```
Press `Ctrl+C` to stop.

### Option B: Using screen (keeps running after SSH disconnect)
```bash
screen -S dopium-bot
./run.sh
# Press Ctrl+A then D to detach
# Reattach with: screen -r dopium-bot
```

### Option C: Using systemd (best for production servers)
See `DEPLOYMENT.md` for detailed instructions.

---

## ⚙️ Setup (First Time Only)

1. **Create `.env` file:**
   ```bash
   nano .env
   ```

2. **Add your bot token:**
   ```env
   BOT_TOKEN=your_bot_token_here
   GROUP_ID=your_group_id
   CHANNEL_USERNAME=your_channel_username
   ```

3. **Install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

## 📝 Useful Commands

| Task | Command |
|------|---------|
| Start bot (background) | `./run_background.sh` |
| Stop bot | `./stop.sh` |
| View logs | `tail -f logs/bot.log` |
| Check if running | `ps aux \| grep "python main.py"` |
| Restart bot | `./stop.sh && ./run_background.sh` |

---

## ❓ Troubleshooting

**Bot not starting?**
- Check `.env` file exists and has `BOT_TOKEN`
- Check logs: `tail -n 50 logs/bot.log`
- Make sure virtual environment is activated

**Bot stops after closing terminal?**
- Use `./run_background.sh` instead of `./run.sh`
- Or use `screen` or `tmux`
- Or set up systemd service (see `DEPLOYMENT.md`)

**Need more help?**
- See `DEPLOYMENT.md` for detailed guide
- Check logs in `logs/bot.log`

