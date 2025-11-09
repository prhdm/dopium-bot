"""Recording flow handler - Orchestrates the recording booking flow with pricing tiers."""
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from domains.recording.use_cases import (
    GetServiceTiersUseCase,
    GetServiceTierOptionsUseCase,
    CompleteBookingUseCase,
)
from config import Settings


class RecordingFlowHandler:
    """
    Handler for recording booking flow.
    
    Orchestrates use cases and handles Telegram-specific logic.
    Follows Single Responsibility - handles recording flow only.
    """
    
    def __init__(
        self,
        get_service_tiers_use_case: GetServiceTiersUseCase,
        get_service_tier_options_use_case: GetServiceTierOptionsUseCase,
        complete_booking_use_case: CompleteBookingUseCase,
    ):
        """Initialize handler with use cases."""
        self._get_tiers = get_service_tiers_use_case
        self._get_tier_options = get_service_tier_options_use_case
        self._complete_booking = complete_booking_use_case
    
    async def start_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
        """Start the recording service flow - show service tier selection."""
        context.user_data["flow_state"] = "recording"
        context.user_data["flow_data"] = {}
        context.user_data["current_step"] = "select_tier"
        
        # Use use case to get service tiers
        tiers = self._get_tiers.execute()
        keyboard = self._create_tier_keyboard(tiers)
        
        return {
            "message": "🎙️ خدمات ضبط (رکورد) و صدابرداری در مجموعه دوپیوم شامل تعرفه های زیر می باشد:\n\n🎙🎙🎙",
            "keyboard": keyboard,
            "next_state": "waiting_tier_selection"
        }
    
    async def process_callback(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        callback_data: str
    ) -> Dict[str, Any]:
        """Process callback query (tier or option selection)."""
        current_step = context.user_data.get("current_step")
        flow_data = context.user_data.get("flow_data", {})
        
        if current_step == "select_tier":
            # Service tier selected
            tier_id = callback_data.replace("tier_select_", "")
            try:
                tier_dto = self._get_tier_options.execute(tier_id)
                
                flow_data["service_tier_id"] = tier_id
                flow_data["service_tier_name"] = tier_dto.name
                context.user_data["flow_data"] = flow_data
                context.user_data["current_step"] = "select_option"
                
                # Create keyboard from options
                keyboard = self._create_option_keyboard(tier_dto.options)
                
                message = tier_dto.name
                if tier_dto.description:
                    message += f"\n\n{tier_dto.description}"
                
                return {
                    "message": message,
                    "keyboard": keyboard,
                    "next_state": "waiting_option_selection"
                }
            except ValueError as e:
                return {"message": f"❌ {str(e)}", "next_state": None}
        
        elif current_step == "select_option":
            # Service option selected
            option_id = callback_data.replace("option_select_", "")
            try:
                # Get tier to find option
                tier_id = flow_data.get("service_tier_id")
                tier_dto = self._get_tier_options.execute(tier_id)
                
                option = next((opt for opt in tier_dto.options if opt.id == option_id), None)
                if not option:
                    return {"message": "❌ گزینه انتخاب شده یافت نشد.", "next_state": None}
                
                flow_data["service_option_id"] = option_id
                flow_data["service_option_name"] = option.name
                flow_data["service_option_price"] = option.price
                flow_data["is_hourly"] = option.is_hourly
                context.user_data["flow_data"] = flow_data
                context.user_data["current_step"] = "get_name"
                
                price_display = f"ساعتی {option.price}" if option.is_hourly else option.price
                
                return {
                    "message": f"✅ {option.name} انتخاب شد\n💰 قیمت: {price_display}\n\n📝 لطفا نام و نام خانوادگی خود را وارد کنید:",
                    "next_state": "waiting_name"
                }
            except ValueError as e:
                return {"message": f"❌ {str(e)}", "next_state": None}
        
        return {"message": "لطفا دوباره تلاش کنید.", "next_state": None}
    
    async def process_input(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user_input: str
    ) -> Dict[str, Any]:
        """Process text input in recording flow (name and contact)."""
        current_step = context.user_data.get("current_step")
        flow_data = context.user_data.get("flow_data", {})
        
        if current_step == "get_name":
            flow_data["user_name"] = user_input
            context.user_data["flow_data"] = flow_data
            context.user_data["current_step"] = "get_contact"
            return {
                "message": "📞 شماره تماس یا ایمیل خود را وارد کنید:",
                "next_state": "waiting_contact"
            }
        
        elif current_step == "get_contact":
            flow_data["user_contact"] = user_input
            context.user_data["flow_data"] = flow_data
            
            # Complete booking using use case
            try:
                from domains.recording.dto import BookingRequestDTO
                
                booking_request = BookingRequestDTO(
                    user_id=update.effective_user.id,
                    user_name=flow_data["user_name"],
                    user_contact=flow_data["user_contact"],
                    service_tier_id=flow_data["service_tier_id"],
                    service_option_id=flow_data["service_option_id"]
                )
                
                booking_response = self._complete_booking.execute(booking_request)
                completion_msg = await self._send_booking_notification(
                    update, context, booking_response
                )
                
                # Clear flow state
                context.user_data["current_step"] = None
                context.user_data["flow_state"] = None
                context.user_data["flow_data"] = {}
                
                return {
                    "message": completion_msg,
                    "next_state": "completed",
                    "completed": True,
                    "restore_keyboard": True
                }
            except ValueError as e:
                return {"message": f"❌ خطا: {str(e)}", "next_state": None}
        
        return {"message": "لطفا دوباره تلاش کنید.", "next_state": None}
    
    async def _send_booking_notification(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        booking_response: "BookingResponseDTO"
    ) -> str:
        """Send booking notification to group."""
        booking_message = booking_response.to_message()
        
        # Send to group if configured
        group_id = Settings.get_group_id()
        if group_id:
            try:
                await context.bot.send_message(
                    chat_id=group_id,
                    text=booking_message
                )
            except Exception as e:
                print(f"Failed to send message to group: {e}")
        
        price_display = f"ساعتی {booking_response.service_option_price}" if booking_response.is_hourly else booking_response.service_option_price
        
        return (
            "✅ رزرو شما با موفقیت ثبت شد!\n\n"
            f"📋 خلاصه رزرو:\n"
            f"• پلن: {booking_response.service_tier_name}\n"
            f"• سرویس: {booking_response.service_option_name}\n"
            f"• قیمت: {price_display}\n"
            f"• تماس شما: {booking_response.user_contact}\n"
            f"• 🔖 کد رهگیری: {booking_response.tracking_code}\n\n"
            f"💳 برای پرداخت و تکمیل سفارش، اطلاعات خود را به پشتیبانی ارسال کنید.\n"
            f"📞 به زودی با شما تماس گرفته خواهد شد."
        )
    
    def _create_tier_keyboard(self, tiers: list) -> InlineKeyboardMarkup:
        """Create inline keyboard for service tier selection."""
        buttons = []
        for tier in tiers:
            buttons.append([
                InlineKeyboardButton(
                    tier.name,
                    callback_data=f"tier_select_{tier.id}"
                )
            ])
        return InlineKeyboardMarkup(buttons)
    
    def _create_option_keyboard(self, options: list) -> InlineKeyboardMarkup:
        """Create inline keyboard for service option selection."""
        buttons = []
        for option in options:
            price_display = f"ساعتی {option.price}" if option.is_hourly else option.price
            button_text = f"{option.name} - {price_display}"
            buttons.append([
                InlineKeyboardButton(
                    button_text,
                    callback_data=f"option_select_{option.id}"
                )
            ])
        return InlineKeyboardMarkup(buttons)
