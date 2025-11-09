"""Admin handler for order confirmation."""
from typing import Dict, Any, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from infrastructure.database.repositories.admin_repository import AdminRepository
from infrastructure.database.repositories.recording_booking_repository import RecordingBookingRepository
from infrastructure.database.repositories.music_production_booking_repository import MusicProductionBookingRepository


class AdminHandler:
    """Handler for admin operations."""
    
    def __init__(self):
        """Initialize admin handler."""
        self._admin_repo = AdminRepository()
        self._recording_booking_repo = RecordingBookingRepository()
        self._music_production_booking_repo = MusicProductionBookingRepository()
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        return self._admin_repo.is_admin(user_id)
    
    def create_admin_keyboard(self) -> ReplyKeyboardMarkup:
        """Create admin reply keyboard."""
        keyboard = [
            [KeyboardButton("تایید سفارش")],
            [KeyboardButton("لغو")]
        ]
        return ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=False
        )
    
    async def show_admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show admin menu."""
        keyboard = self.create_admin_keyboard()
        await update.message.reply_text(
            "👨‍💼 پنل مدیریت\n\n"
            "گزینه مورد نظر را انتخاب کنید:",
            reply_markup=keyboard
        )
    
    async def show_pending_orders(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show list of pending orders."""
        # Get pending recording bookings
        recording_bookings = self._recording_booking_repo.find_by_status("pending")
        music_production_bookings = self._music_production_booking_repo.find_by_status("pending")
        
        if not recording_bookings and not music_production_bookings:
            await update.message.reply_text(
                "✅ هیچ سفارش در انتظار تاییدی وجود ندارد.",
                reply_markup=self.create_admin_keyboard()
            )
            return
        
        # Show recording bookings
        if recording_bookings:
            message = "📋 سفارشات ضبط در انتظار تایید:\n\n"
            buttons = []
            
            for booking in recording_bookings[:10]:  # Show max 10 at a time
                # Parse created_at from string if needed
                if isinstance(booking.created_at, str):
                    from datetime import datetime
                    created_at = datetime.fromisoformat(booking.created_at)
                else:
                    created_at = booking.created_at
                
                booking_info = (
                    f"🔖 کد رهگیری: {booking.tracking_code or 'N/A'}\n"
                    f"👤 {booking.user_name}\n"
                    f"📞 {booking.user_contact}\n"
                    f"📅 {created_at.strftime('%Y-%m-%d %H:%M')}\n"
                )
                message += f"{booking_info}\n{'='*20}\n"
                
                buttons.append([
                    InlineKeyboardButton(
                        f"✅ تایید {booking.tracking_code or booking.id.value[:8]}",
                        callback_data=f"confirm_recording_{booking.id.value}"
                    )
                ])
            
            keyboard = InlineKeyboardMarkup(buttons)
            await update.message.reply_text(message, reply_markup=keyboard)
        
        # Show music production bookings
        if music_production_bookings:
            message = "📋 سفارشات آهنگسازی در انتظار تایید:\n\n"
            buttons = []
            
            for booking in music_production_bookings[:10]:
                # Parse created_at from string if needed
                if isinstance(booking.created_at, str):
                    from datetime import datetime
                    created_at = datetime.fromisoformat(booking.created_at)
                else:
                    created_at = booking.created_at
                
                booking_info = (
                    f"🔖 کد رهگیری: {booking.tracking_code or 'N/A'}\n"
                    f"👤 {booking.user_name}\n"
                    f"📞 {booking.user_contact}\n"
                    f"📅 {created_at.strftime('%Y-%m-%d %H:%M')}\n"
                )
                message += f"{booking_info}\n{'='*20}\n"
                
                buttons.append([
                    InlineKeyboardButton(
                        f"✅ تایید {booking.tracking_code or booking.id.value[:8]}",
                        callback_data=f"confirm_music_{booking.id.value}"
                    )
                ])
            
            keyboard = InlineKeyboardMarkup(buttons)
            await update.message.reply_text(message, reply_markup=keyboard)
        
        await update.message.reply_text(
            "برای بازگشت به منوی مدیریت:",
            reply_markup=self.create_admin_keyboard()
        )
    
    async def confirm_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str) -> None:
        """Confirm an order."""
        query = update.callback_query
        
        # Create BookingId class for repository
        class BookingId:
            def __init__(self, value):
                self.value = value
        
        if callback_data.startswith("confirm_recording_"):
            booking_id = callback_data.replace("confirm_recording_", "")
            booking = self._recording_booking_repo.find_by_id(BookingId(booking_id))
            
            if booking and booking.status == "pending":
                booking.confirm()
                self._recording_booking_repo.save(booking)
                
                await query.edit_message_text(
                    f"✅ سفارش با کد رهگیری {booking.tracking_code} تایید شد!"
                )
                
                # Notify user
                try:
                    await context.bot.send_message(
                        chat_id=booking.user_id,
                        text=(
                            f"✅ سفارش شما تایید شد!\n\n"
                            f"🔖 کد رهگیری: {booking.tracking_code}\n"
                            f"📞 به زودی با شما تماس گرفته خواهد شد."
                        )
                    )
                except Exception as e:
                    print(f"Could not notify user: {e}")
            else:
                await query.answer("❌ سفارش یافت نشد یا قبلا تایید شده است.")
        
        elif callback_data.startswith("confirm_music_"):
            booking_id = callback_data.replace("confirm_music_", "")
            booking = self._music_production_booking_repo.find_by_id(BookingId(booking_id))
            
            if booking and booking.status == "pending":
                booking.confirm()
                self._music_production_booking_repo.save(booking)
                
                await query.edit_message_text(
                    f"✅ سفارش با کد رهگیری {booking.tracking_code} تایید شد!"
                )
                
                # Notify user
                try:
                    await context.bot.send_message(
                        chat_id=booking.user_id,
                        text=(
                            f"✅ سفارش شما تایید شد!\n\n"
                            f"🔖 کد رهگیری: {booking.tracking_code}\n"
                            f"📞 به زودی با شما تماس گرفته خواهد شد."
                        )
                    )
                except Exception as e:
                    print(f"Could not notify user: {e}")
            else:
                await query.answer("❌ سفارش یافت نشد یا قبلا تایید شده است.")
        
        await query.answer()

