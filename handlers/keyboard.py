"""Keyboard handlers."""
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import CallbackQueryHandler, MessageHandler, filters, ContextTypes
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from shared.handlers.flow_manager import FlowManager


def create_inline_keyboard() -> InlineKeyboardMarkup:
    """Create an inline keyboard with 3 buttons."""
    keyboard = [
        [
            InlineKeyboardButton("Button 1", callback_data="button_1"),
            InlineKeyboardButton("Button 2", callback_data="button_2"),
        ],
        [
            InlineKeyboardButton("Button 3", callback_data="button_3"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def create_reply_keyboard() -> ReplyKeyboardMarkup:
    """Create a reply keyboard menu with Persian service buttons."""
    keyboard = [
        [
            KeyboardButton("ضبط"),
            KeyboardButton("آهنگسازی"),
        ],
        [
            KeyboardButton("میکس و مستر"),
            KeyboardButton("مشاوره"),
        ],
        [
            KeyboardButton("خدمات دیستریبیوشن"),
            KeyboardButton("راهنما"),
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="گزینه مورد نظر را انتخاب کنید..."
    )


def create_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Create a keyboard with only cancel button (used during flows)."""
    keyboard = [
        [KeyboardButton("لغو")]
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="برای لغو عملیات، 'لغو' را فشار دهید"
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button callback queries - route to domain handlers."""
    query = update.callback_query
    
    # Only respond in private chats
    if query.message.chat.type != "private":
        await query.answer("❌ این ربات فقط در چت خصوصی کار می‌کند.")
        return
    
    # Check for admin confirm order callbacks
    if query.data.startswith("confirm_"):
        from domains.admin.handlers.admin_handler import AdminHandler
        admin_handler = AdminHandler()
        
        if admin_handler.is_admin(query.from_user.id):
            await admin_handler.confirm_order(update, context, query.data)
            return
        else:
            await query.answer("❌ شما دسترسی مدیریت ندارید.")
            return
    
    # Check if user is in an active flow
    current_flow_state = context.user_data.get("flow_state")
    
    if current_flow_state:
        # User is in a flow, route callback to domain handler
        callback_data = query.data
        await FlowManager.handle_callback(update, context, current_flow_state, callback_data)
    else:
        # Handle old inline buttons (if any)
        if query.data == "button_1":
            await query.answer()
            await query.edit_message_text(text="You pressed Button 1! 🎉")
        elif query.data == "button_2":
            await query.answer()
            await query.edit_message_text(text="You pressed Button 2! 🎉")
        elif query.data == "button_3":
            await query.answer()
            await query.edit_message_text(text="You pressed Button 3! 🎉")
        else:
            await query.answer("❌ این عملیات پشتیبانی نمی‌شود.")


async def handle_reply_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle reply keyboard button presses using domain handlers."""
    # Only respond in private chats
    if update.message.chat.type != "private":
        return
    
    text = update.message.text
    
    # Check for admin commands
    from domains.admin.handlers.admin_handler import AdminHandler
    admin_handler = AdminHandler()
    
    if admin_handler.is_admin(update.effective_user.id):
        if text == "تایید سفارش":
            await admin_handler.show_pending_orders(update, context)
            return
        elif text == "لغو" and not context.user_data.get("flow_state"):
            # Admin cancel - return to main menu
            await update.message.reply_text(
                "لطفا گزینه مورد نظر خود را انتخاب کنید:",
                reply_markup=create_reply_keyboard()
            )
            return
    
    # Check if user is in an active flow
    current_flow_state = context.user_data.get("flow_state")
    
    if current_flow_state:
        # User is in a flow
        if text == "لغو":
            # Cancel the flow and restore main keyboard
            context.user_data["flow_state"] = None
            context.user_data["current_step"] = None
            context.user_data["flow_data"] = {}
            
            main_keyboard = create_reply_keyboard()
            await update.message.reply_text(
                "❌ عملیات لغو شد.\n\nلطفا گزینه مورد نظر خود را انتخاب کنید:",
                reply_markup=main_keyboard
            )
            return
        
        # Process flow input (not cancel)
        user_input = text
        await FlowManager.handle_input(update, context, current_flow_state, user_input)
    else:
        # User clicked a button, start new flow
        # Handle help button separately
        if text == "راهنما":
            await update.message.reply_text("📖 راهنما - راهنمای استفاده از ربات", reply_markup=create_reply_keyboard())
            return
        
        state = FlowManager.get_state_by_button(text)
        if state:
            await FlowManager.handle_start(update, context, state)
        else:
            await update.message.reply_text("لطفا یک گزینه معتبر انتخاب کنید.", reply_markup=create_reply_keyboard())


def register_keyboard_handlers(application) -> None:
    """Register all keyboard handlers with the application."""
    # Register inline keyboard callback handler
    # Note: CallbackQueryHandler doesn't support filters parameter in v20+
    # We check private chat inside the handler instead
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Register reply keyboard handler (for persistent menu buttons)
    # This handles both button clicks and flow inputs (only private chats)
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
            handle_reply_keyboard
        )
    )

