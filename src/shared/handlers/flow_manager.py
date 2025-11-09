"""Flow manager - Routes to domain handlers."""
from typing import Dict, Optional, Callable
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
    def _add_back_button_to_keyboard(cls, keyboard: Optional[InlineKeyboardMarkup], context: ContextTypes.DEFAULT_TYPE) -> Optional[InlineKeyboardMarkup]:
        """Add back button to inline keyboard if there's step history."""
        step_history = context.user_data.get("flow_step_history", [])
        if not step_history:
            return keyboard
        
        # Create back button
        back_button = InlineKeyboardButton("⏪ بازگشت به مرحله قبل", callback_data="flow_back")
        
        if keyboard is None:
            # Create new keyboard with just back button
            return InlineKeyboardMarkup([[back_button]])
        else:
            # Add back button to existing keyboard
            # Convert to list (inline_keyboard can be tuple or list)
            keyboard_buttons = list(keyboard.inline_keyboard)
            keyboard_buttons.append([back_button])
            return InlineKeyboardMarkup(keyboard_buttons)
    
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
            # Initialize step history
            context.user_data["flow_step_history"] = []
            
            result = await handler.start_flow(update, context)
            
            # Track initial step
            current_step = context.user_data.get("current_step")
            if current_step:
                context.user_data["flow_step_history"].append({
                    "step": current_step,
                    "flow_data": context.user_data.get("flow_data", {}).copy()
                })
            
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
            
            # Don't show back button on first step
            cancel_keyboard = cls._create_cancel_keyboard_fn(show_back=False)
            
            if inline_keyboard:
                # Send message with inline keyboard and reply keyboard showing only cancel
                sent_message = await update.message.reply_text(message, reply_markup=inline_keyboard, parse_mode='Markdown')
                # Update reply keyboard to show only cancel button
                await update.message.reply_text("برای لغو عملیات، دکمه 'لغو' را فشار دهید:", reply_markup=cancel_keyboard)
            else:
                await update.message.reply_text(message, reply_markup=cancel_keyboard, parse_mode='Markdown')
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
            # Save current step to history before processing
            current_step = context.user_data.get("current_step")
            flow_data = context.user_data.get("flow_data", {})
            if current_step:
                if "flow_step_history" not in context.user_data:
                    context.user_data["flow_step_history"] = []
                context.user_data["flow_step_history"].append({
                    "step": current_step,
                    "flow_data": flow_data.copy()
                })
            
            result = await handler.process_callback(update, context, callback_data)
            
            query = update.callback_query
            message = result.get("message", "")
            keyboard = result.get("keyboard")
            
            # Add back button if there's history (from step 2 onwards)
            keyboard = cls._add_back_button_to_keyboard(keyboard, context)
            
            if keyboard:
                await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')
            else:
                await query.edit_message_text(message, parse_mode='Markdown')
            
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
            # Save current step to history before processing
            current_step = context.user_data.get("current_step")
            flow_data = context.user_data.get("flow_data", {})
            if current_step:
                if "flow_step_history" not in context.user_data:
                    context.user_data["flow_step_history"] = []
                context.user_data["flow_step_history"].append({
                    "step": current_step,
                    "flow_data": flow_data.copy()
                })
            
            result = await handler.process_input(update, context, user_input)
            
            message = result.get("message", "")
            restore_keyboard = result.get("restore_keyboard", False)
            
            if restore_keyboard and cls._create_reply_keyboard_fn:
                # Flow completed - restore main keyboard
                keyboard = cls._create_reply_keyboard_fn()
                await update.message.reply_text(message, reply_markup=keyboard, parse_mode='Markdown')
            else:
                # Still in flow - show cancel button (back button will be inline on message)
                cancel_keyboard = cls._create_cancel_keyboard_fn(show_back=False)
                
                # Create inline keyboard with back button if there's history
                step_history = context.user_data.get("flow_step_history", [])
                inline_keyboard = None
                if len(step_history) > 0:
                    inline_keyboard = cls._add_back_button_to_keyboard(None, context)
                
                if inline_keyboard:
                    await update.message.reply_text(message, reply_markup=inline_keyboard, parse_mode='Markdown')
                    await update.message.reply_text("برای لغو عملیات، دکمه 'لغو' را فشار دهید:", reply_markup=cancel_keyboard)
                else:
                    await update.message.reply_text(message, reply_markup=cancel_keyboard, parse_mode='Markdown')
            
            # Clear state if completed
            if result.get("completed"):
                context.user_data["flow_state"] = None
                context.user_data["current_step"] = None
                context.user_data["flow_data"] = {}
                context.user_data["flow_step_history"] = []
        else:
            await update.message.reply_text("❌ خطا در پردازش")
    
    @classmethod
    async def handle_back(cls, update: Update, context: ContextTypes.DEFAULT_TYPE, state: str):
        """Handle back button - go back one step in the flow."""
        # Check channel membership
        is_member = await ChannelMembershipValidator.check_membership(update, context)
        if not is_member:
            await ChannelMembershipValidator.send_join_message(update, context)
            return
        
        step_history = context.user_data.get("flow_step_history", [])
        if not step_history:
            # Check if this is a callback query or regular message
            if update.callback_query:
                query = update.callback_query
                await query.answer("❌ نمی‌توانید به عقب برگردید.")
            else:
                await update.message.reply_text("❌ نمی‌توانید به عقب برگردید.")
            return
        
        # Get previous step
        previous_step_data = step_history.pop()
        previous_step = previous_step_data["step"]
        previous_flow_data = previous_step_data["flow_data"]
        
        # Restore previous state
        context.user_data["current_step"] = previous_step
        context.user_data["flow_data"] = previous_flow_data
        
        # Get handler and reconstruct the previous step message
        handler = cls.get_handler_by_state(state)
        if handler:
            # Try to get the message for the previous step
            # For most flows, we can reconstruct based on the step name
            message = ""
            keyboard = None
            
            if previous_step == "select_tier" and hasattr(handler, 'start_flow'):
                # Restart flow to show tier selection
                # Temporarily save flow_data, restart, then restore if needed
                temp_flow_data = context.user_data.get("flow_data", {}).copy()
                result = await handler.start_flow(update, context)
                # Restore flow_data (start_flow might have cleared it)
                context.user_data["flow_data"] = previous_flow_data
                message = result.get("message", "")
                keyboard = result.get("keyboard")
            elif previous_step == "select_option":
                # We need to show the option selection again
                tier_id = previous_flow_data.get("service_tier_id")
                tier_name = previous_flow_data.get("service_tier_name", "")
                if tier_id and hasattr(handler, '_get_tier_options'):
                    # Try to reconstruct option selection screen
                    try:
                        tier_dto = handler._get_tier_options.execute(tier_id)
                        if hasattr(handler, '_create_option_keyboard'):
                            keyboard = handler._create_option_keyboard(tier_dto.options)
                        else:
                            # Fallback: create simple keyboard
                            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                            buttons = []
                            for option in tier_dto.options:
                                buttons.append([InlineKeyboardButton(
                                    option.name,
                                    callback_data=f"option_select_{option.id}"
                                )])
                            keyboard = InlineKeyboardMarkup(buttons) if buttons else None
                        
                        message = tier_name
                        if tier_dto.description:
                            message += f"\n\n{tier_dto.description}"
                    except Exception as e:
                        message = "⏪ به مرحله انتخاب گزینه برگشتید.\n\nلطفا دوباره گزینه مورد نظر را انتخاب کنید."
                        keyboard = None
                else:
                    message = "⏪ به مرحله انتخاب گزینه برگشتید.\n\nلطفا دوباره گزینه مورد نظر را انتخاب کنید."
                    keyboard = None
            elif previous_step == "select_plan":
                # Mix master plan selection - restart flow
                if hasattr(handler, 'start_flow'):
                    temp_flow_data = context.user_data.get("flow_data", {}).copy()
                    result = await handler.start_flow(update, context)
                    context.user_data["flow_data"] = previous_flow_data
                    message = result.get("message", "")
                    keyboard = result.get("keyboard")
            elif previous_step == "select_consultant":
                # Consultation consultant selection - restart flow
                if hasattr(handler, 'start_flow'):
                    temp_flow_data = context.user_data.get("flow_data", {}).copy()
                    result = await handler.start_flow(update, context)
                    context.user_data["flow_data"] = previous_flow_data
                    message = result.get("message", "")
                    keyboard = result.get("keyboard")
            elif previous_step in ["get_name", "get_contact", "get_contact_info", "platforms", "release_date", "contact_info", "waiting_name", "waiting_contact", "waiting_contact_info", "waiting_platforms", "waiting_release_date"]:
                # Text input steps - show appropriate prompt
                step_prompts = {
                    "get_name": "👤 لطفا نام خود را وارد کنید:",
                    "get_contact": "📞 شماره تماس یا ایمیل خود را وارد کنید:",
                    "get_contact_info": "📞 اطلاعات تماس خود را وارد کنید:",
                    "platforms": "پلتفرم‌های مورد نظر برای انتشار را مشخص کنید:\nمثال: Spotify، Apple Music، YouTube Music و...",
                    "release_date": "📅 تاریخ انتشار مورد نظر را وارد کنید (مثلا: 1403/12/15):",
                    "contact_info": "📞 اطلاعات تماس خود را وارد کنید:",
                    "waiting_name": "👤 لطفا نام خود را وارد کنید:",
                    "waiting_contact": "📞 شماره تماس یا ایمیل خود را وارد کنید:",
                    "waiting_contact_info": "📞 اطلاعات تماس خود را وارد کنید:",
                    "waiting_platforms": "پلتفرم‌های مورد نظر برای انتشار را مشخص کنید:\nمثال: Spotify، Apple Music، YouTube Music و...",
                    "waiting_release_date": "📅 تاریخ انتشار مورد نظر را وارد کنید (مثلا: 1403/12/15):"
                }
                message = step_prompts.get(previous_step, "⏪ به مرحله قبلی برگشتید.")
            else:
                message = "⏪ به مرحله قبلی برگشتید."
            
            if not cls._create_cancel_keyboard_fn:
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent.parent))
                from handlers.keyboard import create_cancel_keyboard
                cls._create_cancel_keyboard_fn = create_cancel_keyboard
            
            # Add back button to inline keyboard if there's more history
            keyboard = cls._add_back_button_to_keyboard(keyboard, context)
            
            cancel_keyboard = cls._create_cancel_keyboard_fn(show_back=False)
            
            # Check if this is a callback query (from inline button) or regular message
            if update.callback_query:
                query = update.callback_query
                if keyboard:
                    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')
                else:
                    # Create inline keyboard with just back button if there's more history
                    if len(step_history) > 0:
                        keyboard = cls._add_back_button_to_keyboard(None, context)
                        await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')
                    else:
                        await query.edit_message_text(message, parse_mode='Markdown')
                await query.answer()
            else:
                if keyboard:
                    await update.message.reply_text(message, reply_markup=keyboard, parse_mode='Markdown')
                    await update.message.reply_text("برای لغو عملیات، دکمه 'لغو' را فشار دهید:", reply_markup=cancel_keyboard)
                else:
                    # Create inline keyboard with just back button if there's more history
                    if len(step_history) > 0:
                        keyboard = cls._add_back_button_to_keyboard(None, context)
                        await update.message.reply_text(message, reply_markup=keyboard, parse_mode='Markdown')
                        await update.message.reply_text("برای لغو عملیات، دکمه 'لغو' را فشار دهید:", reply_markup=cancel_keyboard)
                    else:
                        await update.message.reply_text(message, reply_markup=cancel_keyboard, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ خطا در بازگشت به مرحله قبلی.")

