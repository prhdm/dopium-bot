"""Distribution flow handler."""
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


class DistributionFlowHandler:
    """Handler for distribution service flow."""
    
    async def start_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
        """Start the distribution service flow."""
        context.user_data["flow_state"] = "distribution"
        context.user_data["flow_data"] = {}
        context.user_data["current_step"] = "select_pricing"
        
        # Create inline keyboard with pricing options
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "🔵 سالیانه (بدون محدودیت) - 18 میلیون تومان",
                callback_data="pricing_annual"
            )],
            [InlineKeyboardButton(
                "🔵 تک آهنگ - 3 میلیون تومان",
                callback_data="pricing_single"
            )]
        ])
        
        return {
            "message": (
                "سلام وقت بخیر 🔥\n\n"
                "مجموعه دوپیوم از اول تا آخرین مرحله پخش آهنگتون رو انجام میده\n\n"
                "✅ زمان بندی دقیق پخش\n\n"
                "✅ گرفتن کپی رایت های لازم برای آهنگ شما\n\n"
                "✅ پخش جهانی در بیش از 30 پلتفرم معتبر ( اسپاتیفای-اپل موزیک- یوتوب موزیک-تایدال-ساندکلاد-تیک تاک و ... )\n\n"
                "✅ پشتیبانی سریع و دقیق درباره ی درآمدزایی و هرگونه خدمات مربوطه\n\n"
                "________\n\n"
                "برای پخش آثار ، شما میتونید با دوپیوم طبق دو تعرفه زیر همکاری داشته باشید :"
            ),
            "keyboard": keyboard,
            "next_state": "waiting_pricing_selection"
        }
    
    async def process_callback(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        callback_data: str
    ) -> Dict[str, Any]:
        """Process callback query (pricing selection)."""
        current_step = context.user_data.get("current_step")
        flow_data = context.user_data.get("flow_data", {})
        
        if current_step == "select_pricing":
            # Pricing option selected
            pricing_mapping = {
                "pricing_annual": {
                    "name": "سالیانه (بدون محدودیت)",
                    "price": "18 میلیون تومان"
                },
                "pricing_single": {
                    "name": "تک آهنگ",
                    "price": "3 میلیون تومان"
                }
            }
            
            pricing_info = pricing_mapping.get(callback_data)
            if not pricing_info:
                return {"message": "❌ گزینه انتخابی معتبر نیست.", "next_state": None}
            
            flow_data["pricing_id"] = callback_data
            flow_data["pricing_name"] = pricing_info["name"]
            flow_data["pricing_price"] = pricing_info["price"]
            context.user_data["flow_data"] = flow_data
            context.user_data["current_step"] = "platforms"
            
            return {
                "message": (
                    f"✅ تعرفه انتخاب شده:\n"
                    f"{pricing_info['name']}\n"
                    f"💰 قیمت: {pricing_info['price']}\n\n"
                    f"پلتفرم‌های مورد نظر برای انتشار را مشخص کنید:\n"
                    f"مثال: Spotify، Apple Music، YouTube Music و..."
                ),
                "next_state": "waiting_platforms"
            }
        
        return {"message": "لطفا دوباره تلاش کنید.", "next_state": None}
    
    async def process_input(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user_input: str
    ) -> Dict[str, Any]:
        """Process user input in distribution flow."""
        current_step = context.user_data.get("current_step")
        flow_data = context.user_data.get("flow_data", {})
        
        if current_step == "platforms":
            flow_data["platforms"] = user_input
            context.user_data["flow_data"] = flow_data
            context.user_data["current_step"] = "release_date"
            return {
                "message": "📅 تاریخ انتشار مورد نظر را وارد کنید (مثلا: 1403/12/15):",
                "next_state": "waiting_release_date"
            }
        
        elif current_step == "release_date":
            flow_data["release_date"] = user_input
            context.user_data["flow_data"] = flow_data
            context.user_data["current_step"] = "contact_info"
            return {
                "message": "📞 اطلاعات تماس خود را وارد کنید:",
                "next_state": "waiting_contact_info"
            }
        
        elif current_step == "contact_info":
            flow_data["contact_info"] = user_input
            context.user_data["flow_data"] = flow_data
            context.user_data["current_step"] = None
            context.user_data["flow_state"] = None
            
            # Save booking to database
            from datetime import datetime
            from shared.utils.tracking_code import generate_tracking_code
            from infrastructure.database.repositories.distribution_booking_repository import DistributionBookingRepository
            import uuid
            
            user = update.effective_user
            tracking_code = generate_tracking_code(5)
            
            booking_repo = DistributionBookingRepository()
            booking_data = {
                'id': str(uuid.uuid4()),
                'user_id': user.id if user else 0,
                'user_name': flow_data.get('user_name', user.first_name if user else 'نامشخص'),
                'user_contact': flow_data.get('contact_info', 'نامشخص'),
                'pricing_id': flow_data.get('pricing_id'),
                'pricing_name': flow_data.get('pricing_name'),
                'pricing_price': flow_data.get('pricing_price'),
                'platforms': flow_data.get('platforms'),
                'release_date': flow_data.get('release_date'),
                'tracking_code': tracking_code,
                'created_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            flow_data['user_contact'] = flow_data.get('contact_info', 'نامشخص')
            booking_repo.save(booking_data)
            flow_data['tracking_code'] = tracking_code
            
            completion_msg = (
                f"✅ درخواست دیستریبیوشن شما با موفقیت ثبت شد!\n\n"
                f"📋 خلاصه درخواست:\n"
                f"• تعرفه: {flow_data.get('pricing_name', 'نامشخص')}\n"
                f"• قیمت: {flow_data.get('pricing_price', 'نامشخص')}\n"
                f"• پلتفرم‌ها: {flow_data.get('platforms', 'نامشخص')}\n"
                f"• تاریخ انتشار: {flow_data.get('release_date', 'نامشخص')}\n"
                f"• اطلاعات تماس: {flow_data.get('contact_info', 'نامشخص')}\n"
                f"• 🔖 کد رهگیری: `{flow_data.get('tracking_code', 'N/A')}`\n\n"
                f"💳 برای پرداخت و تکمیل سفارش، اطلاعات خود را به پشتیبانی ارسال کنید.\n"
                f"📞 به زودی با شما تماس گرفته خواهد شد."
            )
            
            return {
                "message": completion_msg,
                "next_state": "completed",
                "completed": True,
                "restore_keyboard": True
            }
        
        return {"message": "لطفا دوباره تلاش کنید.", "next_state": None}

