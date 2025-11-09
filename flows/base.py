"""Base flow abstract class."""
from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import ContextTypes
from domains.base import BaseDomain
from services.channel_validator import ChannelValidator


class BaseFlow(ABC):
    """Abstract base class for all conversation flows."""
    
    def __init__(self, domain: BaseDomain):
        self.domain = domain
        self.validator = ChannelValidator()
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle the start of a flow.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        # Check channel membership before starting flow
        is_member = await self.validator.check_membership(update, context)
        if not is_member:
            await self.validator.send_join_message(update, context)
            return
        
        result = await self.domain.start_flow(update, context)
        
        # Send message with optional inline keyboard
        if result.get("keyboard"):
            await update.message.reply_text(
                result["message"],
                reply_markup=result["keyboard"]
            )
        else:
            await update.message.reply_text(result["message"])
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle callback query (inline button clicks).
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        query = update.callback_query
        await query.answer()  # Answer callback to stop loading
        
        # Check channel membership before processing callback
        is_member = await self.validator.check_membership(update, context)
        if not is_member:
            await self.validator.send_join_message(update, context)
            return
        
        # Check if domain has process_callback method
        if hasattr(self.domain, 'process_callback'):
            callback_data = query.data
            result = await self.domain.process_callback(update, context, callback_data)
            
            if result.get("completed"):
                # Flow completed
                from handlers.keyboard import create_reply_keyboard
                await query.message.edit_text(
                    result["message"],
                    reply_markup=None
                )
                await query.message.reply_text(
                    "✅ رزرو تکمیل شد!",
                    reply_markup=create_reply_keyboard()
                )
            elif result.get("keyboard"):
                # Update message with new keyboard
                await query.message.edit_text(
                    result["message"],
                    reply_markup=result["keyboard"]
                )
            else:
                # Update message text only
                await query.message.edit_text(result["message"])
        else:
            await query.message.edit_text("❌ این عملیات پشتیبانی نمی‌شود.")
    
    async def handle_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle user input during a flow.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        # Check channel membership before processing input
        is_member = await self.validator.check_membership(update, context)
        if not is_member:
            await self.validator.send_join_message(update, context)
            return
        
        user_input = update.message.text
        result = await self.domain.process_input(update, context, user_input)
        
        if result.get("completed"):
            # Flow completed, show keyboard again
            from handlers.keyboard import create_reply_keyboard
            reply_markup = create_reply_keyboard() if result.get("restore_keyboard") else None
            await update.message.reply_text(
                result["message"],
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(result["message"])
    
    @abstractmethod
    def get_flow_state_name(self) -> str:
        """Get the name of the flow state for this flow."""
        pass

