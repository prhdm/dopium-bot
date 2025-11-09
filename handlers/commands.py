"""Command handlers."""
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, filters
from handlers.keyboard import create_reply_keyboard
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from domains.admin.handlers.admin_handler import AdminHandler


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    # Only respond in private chats
    if update.message.chat.type != "private":
        return
    
    user = update.effective_user
    admin_handler = AdminHandler()
    
    # Check if user is admin and show admin keyboard
    if admin_handler.is_admin(user.id):
        reply_keyboard = admin_handler.create_admin_keyboard()
        await update.message.reply_text(
            f'👨‍💼 خوش آمدید {user.first_name}! 👋\n\n'
            f'شما به عنوان مدیر دسترسی دارید. از منوی زیر استفاده کنید.',
            reply_markup=reply_keyboard
        )
    else:
        reply_keyboard = create_reply_keyboard()
        # Send message with reply keyboard first
        await update.message.reply_text(
            f'Hello {user.first_name}! 👋\n\n'
            f'Welcome to the bot! Use the menu buttons below or /help to see available commands.',
            reply_markup=reply_keyboard
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    # Only respond in private chats
    if update.message.chat.type != "private":
        return
    
    help_text = """
Available commands:
/start - Start the bot and show keyboard
/keyboard - Show the menu keyboard
/help - Show this help message

Use the menu buttons at the bottom to interact with the bot!
    """
    reply_keyboard = create_reply_keyboard()
    await update.message.reply_text(help_text, reply_markup=reply_keyboard)


async def keyboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the reply keyboard menu."""
    # Only respond in private chats
    if update.message.chat.type != "private":
        return
    
    reply_keyboard = create_reply_keyboard()
    await update.message.reply_text(
        "📱 Showing keyboard menu:",
        reply_markup=reply_keyboard
    )


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin panel command."""
    if update.message.chat.type != "private":
        return
    
    admin_handler = AdminHandler()
    
    if admin_handler.is_admin(update.effective_user.id):
        await admin_handler.show_admin_menu(update, context)
    else:
        await update.message.reply_text("❌ شما دسترسی مدیریت ندارید.")


def register_command_handlers(application) -> None:
    # Only handle commands in private chats
    application.add_handler(CommandHandler("start", start_command, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("help", help_command, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("keyboard", keyboard_command, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("admin", admin_command, filters=filters.ChatType.PRIVATE))

