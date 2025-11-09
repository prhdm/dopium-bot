# Telegram Bot

A Python-based Telegram bot built with `python-telegram-bot` library.

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- A Telegram account
- A bot token from [@BotFather](https://t.me/BotFather)

### 2. Installation

1. Clone or navigate to this repository:
   ```bash
   cd /path/to/Dopium
   ```

2. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Configuration

1. Get your bot token from [@BotFather](https://t.me/BotFather):
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` command
   - Follow the instructions to create a new bot
   - Copy the token you receive

2. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and add your bot token and optional group ID:
   ```
   BOT_TOKEN=your_actual_bot_token_here
   GROUP_ID=your_group_id_here  # Optional: for welcome messages
   ```

### 4. Running the Bot

```bash
python main.py
```

You should see a message indicating the bot is starting, and your bot will be online!

## Features

- `/start` - Welcome message
- `/help` - Show available commands
- Echo messages - Replies to text messages
- Automatic welcome message to group on startup (if GROUP_ID is set)

## Project Structure

The project follows clean architecture principles with separated concerns:

```
Dopium/
├── main.py                 # Main entry point
├── config/                 # Configuration module
│   ├── __init__.py
│   └── settings.py         # Environment variables and settings
├── handlers/               # Bot handlers
│   ├── __init__.py
│   ├── commands.py         # Command handlers (/start, /help, etc.)
│   └── messages.py         # Message handlers (echo, etc.)
├── core/                   # Core application logic
│   ├── __init__.py
│   ├── bot.py              # Bot application setup
│   └── lifecycle.py        # Lifecycle hooks (post_init, etc.)
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Architecture

The project is organized using clean architecture principles:

- **Config Layer** (`config/`): Handles all configuration and environment variables
- **Handlers Layer** (`handlers/`): Contains all bot command and message handlers
- **Core Layer** (`core/`): Contains application setup and lifecycle management
- **Main Entry Point** (`main.py`): Orchestrates the application startup

## Extending the Bot

### Adding New Commands

Add new command handlers in `handlers/commands.py`:

```python
async def my_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /my_command."""
    await update.message.reply_text("Response")

# Then register it in register_command_handlers()
application.add_handler(CommandHandler("my_command", my_command))
```

### Adding New Message Handlers

Add new message handlers in `handlers/messages.py`:

```python
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle image messages."""
    # Your logic here

# Then register it in register_message_handlers()
application.add_handler(MessageHandler(filters.PHOTO, handle_image))
```

The bot uses the `python-telegram-bot` library. Refer to the [official documentation](https://python-telegram-bot.org/) for more advanced features.

## License

This project is open source and available for personal use.

