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
from infrastructure.database.repositories.mix_master_booking_repository import MixMasterBookingRepository
from infrastructure.database.repositories.consultation_booking_repository import ConsultationBookingRepository
from infrastructure.database.repositories.distribution_booking_repository import DistributionBookingRepository


class AdminHandler:
    """Handler for admin operations."""
    
    def __init__(self):
        """Initialize admin handler."""
        self._admin_repo = AdminRepository()
        self._recording_booking_repo = RecordingBookingRepository()
        self._music_production_booking_repo = MusicProductionBookingRepository()
        self._mix_master_booking_repo = MixMasterBookingRepository()
        self._consultation_booking_repo = ConsultationBookingRepository()
        self._distribution_booking_repo = DistributionBookingRepository()
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        return self._admin_repo.is_admin(user_id)
    
    def add_admin(self, user_id: int, username: str = None, full_name: str = None) -> bool:
        """Add a new admin user."""
        return self._admin_repo.add_admin(user_id, username, full_name)
    
    def remove_admin(self, user_id: int) -> bool:
        """Remove an admin user."""
        return self._admin_repo.remove_admin(user_id)
    
    def get_all_admins(self) -> list:
        """Get all active admin users."""
        return self._admin_repo.get_all_admins()
    
    def create_admin_keyboard(self) -> ReplyKeyboardMarkup:
        """Create admin reply keyboard."""
        keyboard = [
            [KeyboardButton("تایید سفارش")],
            [KeyboardButton("جستجوی سفارش")],
            [KeyboardButton("تاریخچه سفارشات")]
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
    
    async def search_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Prompt admin to enter tracking code for search."""
        context.user_data["admin_search_mode"] = True
        await update.message.reply_text(
            "🔍 جستجوی سفارش\n\n"
            "لطفا کد رهگیری سفارش را وارد کنید:",
            reply_markup=self.create_admin_keyboard()
        )
    
    async def handle_search_input(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        tracking_code: str
    ) -> None:
        """Handle search input and show order if found."""
        # Create BookingId class for repository
        class BookingId:
            def __init__(self, value):
                self.value = value
        
        # Search in recording bookings
        recording_booking = self._recording_booking_repo.find_by_tracking_code(tracking_code)
        if recording_booking:
            # Parse created_at from string if needed
            if isinstance(recording_booking.created_at, str):
                from datetime import datetime
                created_at = datetime.fromisoformat(recording_booking.created_at)
            else:
                created_at = recording_booking.created_at
            
            booking_info = (
                f"📋 سفارش ضبط\n\n"
                f"🔖 کد رهگیری: `{recording_booking.tracking_code or 'N/A'}`\n"
                f"👤 {recording_booking.user_name}\n"
                f"📞 {recording_booking.user_contact}\n"
                f"📅 {created_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"📊 وضعیت: {recording_booking.status}\n"
            )
            
            keyboard = None
            if recording_booking.status == "pending":
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        f"✅ تایید {recording_booking.tracking_code or recording_booking.id.value[:8]}",
                        callback_data=f"confirm_recording_{recording_booking.id.value}"
                    )]
                ])
            
            await update.message.reply_text(
                booking_info,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            context.user_data["admin_search_mode"] = False
            return
        
        # Search in music production bookings
        music_booking = self._music_production_booking_repo.find_by_tracking_code(tracking_code)
        if music_booking:
            # Parse created_at from string if needed
            if isinstance(music_booking.created_at, str):
                from datetime import datetime
                created_at = datetime.fromisoformat(music_booking.created_at)
            else:
                created_at = music_booking.created_at
            
            booking_info = (
                f"📋 سفارش آهنگسازی\n\n"
                f"🔖 کد رهگیری: `{music_booking.tracking_code or 'N/A'}`\n"
                f"👤 {music_booking.user_name}\n"
                f"📞 {music_booking.user_contact}\n"
                f"📅 {created_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"📊 وضعیت: {music_booking.status}\n"
            )
            
            keyboard = None
            if music_booking.status == "pending":
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        f"✅ تایید {music_booking.tracking_code or music_booking.id.value[:8]}",
                        callback_data=f"confirm_music_{music_booking.id.value}"
                    )]
                ])
            
            await update.message.reply_text(
                booking_info,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            context.user_data["admin_search_mode"] = False
            return
        
        # Not found
        await update.message.reply_text(
            f"❌ سفارشی با کد رهگیری `{tracking_code}` یافت نشد.",
            parse_mode='Markdown',
            reply_markup=self.create_admin_keyboard()
        )
        context.user_data["admin_search_mode"] = False
    
    async def show_order_history_categories(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show order history categories."""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 همه سفارشات", callback_data="history_all")],
            [InlineKeyboardButton("📋 ضبط", callback_data="history_recording")],
            [InlineKeyboardButton("🎵 آهنگسازی", callback_data="history_music_production")],
            [InlineKeyboardButton("🎛 میکس و مستر", callback_data="history_mix_master")],
            [InlineKeyboardButton("💡 مشاوره", callback_data="history_consultation")],
            [InlineKeyboardButton("📦 دیستریبیوشن", callback_data="history_distribution")]
        ])
        
        message_obj = update.message if update.message else (update.callback_query.message if update.callback_query else None)
        if message_obj:
            if update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.message.edit_text(
                    "📊 تاریخچه سفارشات\n\n"
                    "لطفا دسته‌بندی مورد نظر را انتخاب کنید:",
                    reply_markup=keyboard
                )
            else:
                await message_obj.reply_text(
                    "📊 تاریخچه سفارشات\n\n"
                    "لطفا دسته‌بندی مورد نظر را انتخاب کنید:",
                    reply_markup=keyboard
                )
    
    async def show_order_history(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        category: str,
        page: int = 0
    ) -> None:
        """Show order history for a specific category with pagination."""
        from datetime import datetime
        
        # Get the message object (works for both regular messages and callback queries)
        message_obj = update.message if update.message else (update.callback_query.message if update.callback_query else None)
        if not message_obj:
            return
        
        # Handle pagination callbacks
        if update.callback_query and update.callback_query.data.startswith("history_page_"):
            # Extract category and page from callback data
            parts = update.callback_query.data.replace("history_page_", "").split("_")
            if len(parts) >= 2:
                category = parts[0]
                try:
                    page = int(parts[1])
                except ValueError:
                    page = 0
        
        # Get all bookings from all categories
        all_bookings = []
        
        # Recording bookings
        recording_bookings = self._recording_booking_repo.find_all()
        for booking in recording_bookings:
            all_bookings.append(("recording", booking))
        
        # Music production bookings
        music_bookings = self._music_production_booking_repo.find_all()
        for booking in music_bookings:
            all_bookings.append(("music_production", booking))
        
        # Mix master bookings
        mix_master_bookings = self._mix_master_booking_repo.find_all()
        for booking in mix_master_bookings:
            all_bookings.append(("mix_master", booking))
        
        # Consultation bookings
        consultation_bookings = self._consultation_booking_repo.find_all()
        for booking in consultation_bookings:
            all_bookings.append(("consultation", booking))
        
        # Distribution bookings
        distribution_bookings = self._distribution_booking_repo.find_all()
        for booking in distribution_bookings:
            all_bookings.append(("distribution", booking))
        
        # Sort by created_at (newest first)
        def get_created_at(booking_item):
            booking = booking_item[1]
            if isinstance(booking, dict):
                created_at_str = booking.get('created_at', '')
            else:
                created_at_str = booking.created_at if hasattr(booking, 'created_at') else ''
            
            if isinstance(created_at_str, datetime):
                return created_at_str
            try:
                return datetime.fromisoformat(created_at_str)
            except:
                return datetime.min
        
        all_bookings.sort(key=get_created_at, reverse=True)
        
        # Filter by category if needed
        if category == "recording":
            all_bookings = [b for b in all_bookings if b[0] == "recording"]
        elif category == "music_production":
            all_bookings = [b for b in all_bookings if b[0] == "music_production"]
        elif category == "mix_master":
            all_bookings = [b for b in all_bookings if b[0] == "mix_master"]
        elif category == "consultation":
            all_bookings = [b for b in all_bookings if b[0] == "consultation"]
        elif category == "distribution":
            all_bookings = [b for b in all_bookings if b[0] == "distribution"]
        # "all" shows everything (already combined)
        
        if not all_bookings:
            await message_obj.reply_text(
                "✅ هیچ سفارشی در تاریخچه وجود ندارد.",
                reply_markup=self.create_admin_keyboard()
            )
            return
        
        # Pagination: 5 items per page
        items_per_page = 5
        total_pages = (len(all_bookings) + items_per_page - 1) // items_per_page
        page = max(0, min(page, total_pages - 1))
        
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        page_bookings = all_bookings[start_idx:end_idx]
        
        # Category labels
        cat_labels = {
            "recording": "📋 ضبط",
            "music_production": "🎵 آهنگسازی",
            "mix_master": "🎛 میکس و مستر",
            "consultation": "💡 مشاوره",
            "distribution": "📦 دیستریبیوشن"
        }
        
        # Build message
        category_name = cat_labels.get(category, "همه")
        message = f"📊 تاریخچه سفارشات {category_name}\n\n"
        
        for cat, booking in page_bookings:
            # Handle both dict and object bookings
            if isinstance(booking, dict):
                created_at_str = booking.get('created_at', '')
                tracking_code = booking.get('tracking_code')
                user_name = booking.get('user_name', 'نامشخص')
                user_contact = booking.get('user_contact', 'نامشخص')
                status = booking.get('status', 'pending')
                # Get pricing info for distribution
                pricing_name = booking.get('pricing_name')
                pricing_price = booking.get('pricing_price')
            else:
                created_at_str = booking.created_at if hasattr(booking, 'created_at') else ''
                tracking_code = booking.tracking_code if hasattr(booking, 'tracking_code') else None
                user_name = booking.user_name if hasattr(booking, 'user_name') else 'نامشخص'
                user_contact = booking.user_contact if hasattr(booking, 'user_contact') else 'نامشخص'
                status = booking.status if hasattr(booking, 'status') else 'pending'
                pricing_name = getattr(booking, 'pricing_name', None) if hasattr(booking, 'pricing_name') else None
                pricing_price = getattr(booking, 'pricing_price', None) if hasattr(booking, 'pricing_price') else None
            
            # Parse created_at
            if isinstance(created_at_str, datetime):
                created_at = created_at_str
            else:
                try:
                    created_at = datetime.fromisoformat(created_at_str)
                except:
                    created_at = datetime.now()
            
            cat_label = cat_labels.get(cat, cat)
            status_emoji = "✅" if status == "confirmed" else "⏳" if status == "pending" else "❌"
            
            booking_info = (
                f"{cat_label} {status_emoji}\n"
                f"🔖 کد رهگیری: `{tracking_code or 'N/A'}`\n"
            )
            
            # Add pricing info for distribution bookings
            if cat == "distribution" and pricing_name:
                booking_info += f"💰 تعرفه: {pricing_name} ({pricing_price or ''})\n"
            
            booking_info += (
                f"👤 {user_name}\n"
                f"📞 {user_contact}\n"
                f"📅 {created_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"📊 وضعیت: {status}\n"
            )
            message += f"{booking_info}\n{'='*20}\n"
        
        message += f"\n📄 صفحه {page + 1} از {total_pages} ({len(all_bookings)} سفارش)"
        
        # Create navigation keyboard
        keyboard_buttons = []
        nav_row = []
        
        if page > 0:
            nav_row.append(InlineKeyboardButton(
                "◀️ قبلی",
                callback_data=f"history_page_{category}_{page - 1}"
            ))
        
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton(
                "▶️ بعدی",
                callback_data=f"history_page_{category}_{page + 1}"
            ))
        
        if nav_row:
            keyboard_buttons.append(nav_row)
        
        keyboard_buttons.append([InlineKeyboardButton(
            "🔙 بازگشت به دسته‌بندی‌ها",
            callback_data="history_categories"
        )])
        
        keyboard = InlineKeyboardMarkup(keyboard_buttons) if keyboard_buttons else None
        
        # If it's a callback query, edit the message, otherwise reply
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.message.edit_text(
                message,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        else:
            await message_obj.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
    
    async def show_pending_orders(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show list of pending orders."""
        # Get pending recording bookings
        recording_bookings = self._recording_booking_repo.find_by_status("pending")
        music_production_bookings = self._music_production_booking_repo.find_by_status("pending")
        
        # Debug: Log the number of orders found
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Admin {update.effective_user.id} viewing orders: {len(recording_bookings)} recording, {len(music_production_bookings)} music production")
        
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
                    f"🔖 کد رهگیری: `{booking.tracking_code or 'N/A'}`\n"
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
            await update.message.reply_text(message, reply_markup=keyboard, parse_mode='Markdown')
        
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
                    f"🔖 کد رهگیری: `{booking.tracking_code or 'N/A'}`\n"
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
            await update.message.reply_text(message, reply_markup=keyboard, parse_mode='Markdown')
        
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
                    f"✅ سفارش با کد رهگیری `{booking.tracking_code}` تایید شد!",
                    parse_mode='Markdown'
                )
                
                # Notify user
                try:
                    await context.bot.send_message(
                        chat_id=booking.user_id,
                        text=(
                            f"✅ سفارش شما تایید شد!\n\n"
                            f"🔖 کد رهگیری: `{booking.tracking_code}`\n"
                            f"📞 به زودی با شما تماس گرفته خواهد شد."
                        ),
                        parse_mode='Markdown'
                    )
                    
                    # Send additional instructions for recording
                    await context.bot.send_message(
                        chat_id=booking.user_id,
                        text=(
                            "خیلی ممنون که مجموعه مارو برای ضبط آهنگت انتخاب کردی\n\n"
                            "برای اینکه بتونیم پروسه کار رو به بهترین نحو ممکن ببریم جلو و یه ضبط خفن داشته باشیم چندتا نکته هست که ممنون میشم بخونی\n\n"
                            "۱ - قبل از ضبطت سعی کن استرس و اینارو از خودت دور کنی و برای یه رکورد مشتی و جون دار آماده باش🤝✅\n\n"
                            "۲ - حتما سر ساعت مقرر بیا استودیو چون قطعا قبل و بعد شما رفقا تایم دارن برای ضبط و باید به حقوق اونا احترام بذاریم 😅\n\n"
                            "۳ - از آوردن همراه خودداری کن و خودت تنها بیا پیشمون که بتونی با صدابردار بیشترین تمرکز رو روی ضبط داشته باشی🤓\n\n"
                            "۴ - قبل ضبط یه لیوان آب بزن و گلو رو صاف و صوف کن 🫖\n\n"
                            "۵ - ما از خدامونه که بشینیم ساعت ها گپ بزنیم راجب موزیک و عشق و حال کنیم ؛\n"
                            "ولی چون اینجا هرروز پر از رفیقایی میشه که باید به کارشون رسیدگی بشه\n"
                            "و ما هم یه مجموعه‌ی نقلی ایم\n"
                            "ضبطت که تموم شد استودیو رو برای نفر بعدی بذار\n\n"
                            "تشکر زیاد ❤️🥃🙏🏼"
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
                    f"✅ سفارش با کد رهگیری `{booking.tracking_code}` تایید شد!",
                    parse_mode='Markdown'
                )
                
                # Notify user
                try:
                    await context.bot.send_message(
                        chat_id=booking.user_id,
                        text=(
                            f"✅ سفارش شما تایید شد!\n\n"
                            f"🔖 کد رهگیری: `{booking.tracking_code}`\n"
                            f"📞 به زودی با شما تماس گرفته خواهد شد."
                        ),
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    print(f"Could not notify user: {e}")
            else:
                await query.answer("❌ سفارش یافت نشد یا قبلا تایید شده است.")
        
        await query.answer()

