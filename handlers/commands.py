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
        # Send welcome message with reply keyboard
        await update.message.reply_text(
            'سلام رفیق 🫡🔥\n\n'
            'ازینکه مجموعه دوپیوم رو انتخاب\n'
            'کردی ازت ممنونیم 🤝\n\n'
            'برای دریافت خدمات یکی از گزینه‌‌هارو انتخاب کن و بریم تو کارش',
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


async def addadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add an admin user. Usage: /addadmin <user_id> or /addadmin @username or reply to a message with /addadmin"""
    if update.message.chat.type != "private":
        return
    
    admin_handler = AdminHandler()
    requester_id = update.effective_user.id
    
    # Check if requester is admin
    if not admin_handler.is_admin(requester_id):
        await update.message.reply_text("❌ شما دسترسی مدیریت ندارید.")
        return
    
    # Check if replying to a message
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        target_user = update.message.reply_to_message.from_user
        user_id = target_user.id
        username = target_user.username
        full_name = f"{target_user.first_name or ''} {target_user.last_name or ''}".strip()
    else:
        # Try to get user_id from command arguments
        args = context.args
        if not args or len(args) == 0:
            await update.message.reply_text(
                "📝 استفاده:\n"
                "• `/addadmin <user_id>` - اضافه کردن ادمین با شناسه کاربری\n"
                "• `/addadmin @username` - اضافه کردن ادمین با نام کاربری (نیاز به تعامل قبلی)\n"
                "• پاسخ به پیام کاربر با `/addadmin` - اضافه کردن کاربر به عنوان ادمین",
                parse_mode='Markdown'
            )
            return
        
        arg = args[0]
        
        # Check if it's a username (starts with @)
        if arg.startswith('@'):
            username = arg[1:]
            # Try to get user info from bot's chat members (if in a group/channel)
            # Note: This only works if the user has interacted with the bot or is in a shared chat
            try:
                # Try to get user by username from a group/channel if available
                from config import Settings
                group_id = Settings.get_group_id()
                channel_id = Settings.get_channel_id()
                
                user_id = None
                full_name = None
                
                # Try group first
                if group_id:
                    try:
                        member = await context.bot.get_chat_member(group_id, username)
                        user_id = member.user.id
                        full_name = f"{member.user.first_name or ''} {member.user.last_name or ''}".strip()
                    except:
                        pass
                
                # Try channel if group didn't work
                if not user_id and channel_id:
                    try:
                        member = await context.bot.get_chat_member(channel_id, username)
                        user_id = member.user.id
                        full_name = f"{member.user.first_name or ''} {member.user.last_name or ''}".strip()
                    except:
                        pass
                
                if not user_id:
                    await update.message.reply_text(
                        f"❌ نمی‌توانم کاربر @{username} را پیدا کنم.\n\n"
                        f"💡 راه‌حل:\n"
                        f"• کاربر باید حداقل یک بار با ربات چت کرده باشد\n"
                        f"• یا در گروه/کانال مشترک با ربات باشد\n"
                        f"• یا از شناسه عددی کاربر استفاده کنید (می‌توانید از @userinfobot استفاده کنید)",
                        parse_mode='Markdown'
                    )
                    return
            except Exception as e:
                await update.message.reply_text(
                    f"❌ خطا در پیدا کردن کاربر: {str(e)}\n\n"
                    f"💡 لطفا از شناسه عددی کاربر استفاده کنید.",
                    parse_mode='Markdown'
                )
                return
        else:
            # Try to parse as user_id
            try:
                user_id = int(arg)
                username = None
                full_name = None
            except ValueError:
                await update.message.reply_text(
                    "❌ شناسه کاربری باید یک عدد باشد یا نام کاربری با @ شروع شود.\n\n"
                    "💡 مثال:\n"
                    "• `/addadmin 123456789`\n"
                    "• `/addadmin @username`",
                    parse_mode='Markdown'
                )
                return
    
    # Add admin
    success = admin_handler.add_admin(user_id, username, full_name)
    
    if success:
        message = f"✅ کاربر با شناسه `{user_id}` به عنوان ادمین اضافه شد."
        if username:
            message += f"\nنام کاربری: @{username}"
        if full_name:
            message += f"\nنام: {full_name}"
        await update.message.reply_text(message, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ خطا در اضافه کردن ادمین.")


async def removeadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove an admin user. Usage: /removeadmin <user_id>"""
    if update.message.chat.type != "private":
        return
    
    admin_handler = AdminHandler()
    requester_id = update.effective_user.id
    
    # Check if requester is admin
    if not admin_handler.is_admin(requester_id):
        await update.message.reply_text("❌ شما دسترسی مدیریت ندارید.")
        return
    
    args = context.args
    if not args or len(args) == 0:
        await update.message.reply_text(
            "📝 استفاده: `/removeadmin <user_id>`",
            parse_mode='Markdown'
        )
        return
    
    try:
        user_id = int(args[0])
    except ValueError:
        await update.message.reply_text("❌ شناسه کاربری باید یک عدد باشد.")
        return
    
    # Don't allow removing yourself
    if user_id == requester_id:
        await update.message.reply_text("❌ نمی‌توانید خودتان را حذف کنید.")
        return
    
    # Remove admin
    success = admin_handler.remove_admin(user_id)
    
    if success:
        await update.message.reply_text(
            f"✅ کاربر با شناسه `{user_id}` از لیست ادمین‌ها حذف شد.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ خطا در حذف ادمین.")


async def listadmins_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all admin users."""
    if update.message.chat.type != "private":
        return
    
    admin_handler = AdminHandler()
    requester_id = update.effective_user.id
    
    # Check if requester is admin
    if not admin_handler.is_admin(requester_id):
        await update.message.reply_text("❌ شما دسترسی مدیریت ندارید.")
        return
    
    admins = admin_handler.get_all_admins()
    
    if not admins:
        await update.message.reply_text("📋 هیچ ادمینی در سیستم ثبت نشده است.")
        return
    
    message = "📋 لیست ادمین‌ها:\n\n"
    for admin in admins:
        user_id, username, full_name, created_at = admin
        username_display = f"@{username}" if username else "بدون نام کاربری"
        name_display = full_name if full_name else "بدون نام"
        message += f"• شناسه: `{user_id}`\n"
        message += f"  نام کاربری: {username_display}\n"
        message += f"  نام: {name_display}\n"
        message += f"  تاریخ اضافه شدن: {created_at}\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')


def register_command_handlers(application) -> None:
    # Only handle commands in private chats
    application.add_handler(CommandHandler("start", start_command, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("help", help_command, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("keyboard", keyboard_command, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("admin", admin_command, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("addadmin", addadmin_command, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("removeadmin", removeadmin_command, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("listadmins", listadmins_command, filters=filters.ChatType.PRIVATE))

