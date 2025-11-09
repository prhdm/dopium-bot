"""Flow manager - Routes to domain handlers."""
from typing import Dict, Optional, Callable
from telegram import Update
from telegram.ext import ContextTypes
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from shared.services.channel_validator import ChannelMembershipValidator


class FlowManager:
    """Manages flows and routes to domain handlers."""
    
    # Map button text to flow state
    BUTTON_TO_STATE: Dict[str, str] = {
        "ضبط": "recording",
        "آهنگسازی": "music_production",
        "میکس و مستر": "mix_master",
        "مشاوره": "consultation",
        "خدمات دیستریبیوشن": "distribution",
    }
    
    # Handlers will be initialized here
    _handlers: Dict[str, any] = {}
    _create_reply_keyboard_fn: Optional[Callable] = None
    _create_cancel_keyboard_fn: Optional[Callable] = None
    
    @classmethod
    def register_handler(cls, state: str, handler):
        """Register a handler for a flow state."""
        cls._handlers[state] = handler
    
    @classmethod
    def set_reply_keyboard_creator(cls, create_fn: Callable):
        """Set the function to create reply keyboard."""
        cls._create_reply_keyboard_fn = create_fn
    
    @classmethod
    def set_cancel_keyboard_creator(cls, create_fn: Callable):
        """Set the function to create cancel keyboard."""
        cls._create_cancel_keyboard_fn = create_fn
    
    @classmethod
    def get_handler_by_state(cls, state: str):
        """Get handler by flow state."""
        return cls._handlers.get(state)
    
    @classmethod
    def get_state_by_button(cls, button_text: str) -> Optional[str]:
        """Get flow state by button text."""
        return cls.BUTTON_TO_STATE.get(button_text)
    
    @classmethod
    async def handle_start(cls, update: Update, context: ContextTypes.DEFAULT_TYPE, state: str):
        """Start a flow."""
        # Check channel membership before starting flow
        is_member = await ChannelMembershipValidator.check_membership(update, context)
        if not is_member:
            await ChannelMembershipValidator.send_join_message(update, context)
            return
        
        handler = cls.get_handler_by_state(state)
        if handler:
            result = await handler.start_flow(update, context)
            
            # Send message with inline keyboard (if any) and cancel button
            message = result.get("message", "")
            inline_keyboard = result.get("keyboard")
            
            if not cls._create_cancel_keyboard_fn:
                # Import cancel keyboard creator if not set
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent.parent))
                from handlers.keyboard import create_cancel_keyboard
                cls._create_cancel_keyboard_fn = create_cancel_keyboard
            
            cancel_keyboard = cls._create_cancel_keyboard_fn()
            
            if inline_keyboard:
                # Send message with inline keyboard and reply keyboard showing only cancel
                sent_message = await update.message.reply_text(message, reply_markup=inline_keyboard)
                # Update reply keyboard to show only cancel button
                await update.message.reply_text("برای لغو عملیات، دکمه 'لغو' را فشار دهید:", reply_markup=cancel_keyboard)
            else:
                await update.message.reply_text(message, reply_markup=cancel_keyboard)
        else:
            await update.message.reply_text("❌ این سرویس در حال حاضر در دسترس نیست.")
    
    @classmethod
    async def handle_callback(cls, update: Update, context: ContextTypes.DEFAULT_TYPE, state: str, callback_data: str):
        """Handle callback query."""
        # Check channel membership before processing callback
        is_member = await ChannelMembershipValidator.check_membership(update, context)
        if not is_member:
            query = update.callback_query
            await ChannelMembershipValidator.send_join_message(update, context)
            await query.answer("لطفا ابتدا در کانال عضو شوید.")
            return
        
        handler = cls.get_handler_by_state(state)
        if handler and hasattr(handler, 'process_callback'):
            result = await handler.process_callback(update, context, callback_data)
            
            query = update.callback_query
            message = result.get("message", "")
            keyboard = result.get("keyboard")
            
            if keyboard:
                await query.edit_message_text(message, reply_markup=keyboard)
            else:
                await query.edit_message_text(message)
            
            await query.answer()
        else:
            query = update.callback_query
            await query.answer("❌ خطا در پردازش")
    
    @classmethod
    async def handle_input(cls, update: Update, context: ContextTypes.DEFAULT_TYPE, state: str, user_input: str):
        """Handle text input."""
        # Check channel membership before processing input
        is_member = await ChannelMembershipValidator.check_membership(update, context)
        if not is_member:
            await ChannelMembershipValidator.send_join_message(update, context)
            return
        
        if not cls._create_cancel_keyboard_fn:
            # Import cancel keyboard creator if not set
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from handlers.keyboard import create_cancel_keyboard
            cls._create_cancel_keyboard_fn = create_cancel_keyboard
        
        handler = cls.get_handler_by_state(state)
        if handler and hasattr(handler, 'process_input'):
            result = await handler.process_input(update, context, user_input)
            
            message = result.get("message", "")
            restore_keyboard = result.get("restore_keyboard", False)
            
            if restore_keyboard and cls._create_reply_keyboard_fn:
                # Flow completed - restore main keyboard
                keyboard = cls._create_reply_keyboard_fn()
                await update.message.reply_text(message, reply_markup=keyboard)
            else:
                # Still in flow - show cancel button
                cancel_keyboard = cls._create_cancel_keyboard_fn()
                await update.message.reply_text(message, reply_markup=cancel_keyboard)
            
            # Clear state if completed
            if result.get("completed"):
                context.user_data["flow_state"] = None
                context.user_data["current_step"] = None
                context.user_data["flow_data"] = {}
        else:
            await update.message.reply_text("❌ خطا در پردازش")

