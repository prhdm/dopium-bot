"""Consultation flow handler."""
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


class ConsultationFlowHandler:
    """Handler for consultation service flow."""
    
    async def start_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
        """Start the consultation service flow."""
        context.user_data["flow_state"] = "consultation"
        context.user_data["flow_data"] = {}
        context.user_data["current_step"] = "select_consultant"
        
        # Create inline keyboard with consultant options
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "۱) معراج ناجی",
                callback_data="consultant_meraj"
            )],
            [InlineKeyboardButton(
                "۲) اشکان آکای (پروف کی)",
                callback_data="consultant_ashkan"
            )],
            [InlineKeyboardButton(
                "۳) اشکورت",
                callback_data="consultant_ashkort"
            )]
        ])
        
        return {
            "message": (
                "⚪️ مشاوره\n\n"
                "توی دوپیوم من می تونم براتون یه جلسه مشاوره دو نفری ست کنم که مفصل صحبت کنیم. مشاور های مجموعه : معراج ناجی و اشکان آکای و اشکورت شرایط به این شکل هستش که تشریف میارید دفتر برای جلسه حضوری و مفصل صحبت می کنیم\n\n"
                "___________________________\n\n"
                "🟢 کریر کاری تون بررسی میشه\n\n"
                "🟢 ترک ها گوش داده میشه\n\n"
                "🟢 نکات مثبت و منفی رو میاریم روی کاغذ\n\n"
                "🟢 پلن های مناسب پخش بر طبق کانسپت کاری تون رو بهتون پیشنهاد میدیم\n\n"
                "___________________\n\n"
                "جلسات به صورت خصوصی برگزار میشه ( 📍 برای بکس تهران به صورت حضوری و برای بقیه بچه ها به صورت آنلاین ) و تو یک فضای آکادمیک و تئوریک شرایط رو تحلیل می کنیم و هیچ محدودیت تایمی هم نداره ! هزینه هر جلسه ۱/۵۰۰ هستش و خب قابلتون رو هم نداره ⭐️\n\n"
                "گزینه ی انتخاب مشاور:"
            ),
            "keyboard": keyboard,
            "next_state": "waiting_consultant_selection"
        }
    
    async def process_callback(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        callback_data: str
    ) -> Dict[str, Any]:
        """Process callback query (consultant selection)."""
        current_step = context.user_data.get("current_step")
        flow_data = context.user_data.get("flow_data", {})
        
        if current_step == "select_consultant":
            # Consultant selected
            consultant_mapping = {
                "consultant_meraj": {
                    "name": "معراج ناجی"
                },
                "consultant_ashkan": {
                    "name": "اشکان آکای (پروف کی)"
                },
                "consultant_ashkort": {
                    "name": "اشکورت"
                }
            }
            
            consultant_info = consultant_mapping.get(callback_data)
            if not consultant_info:
                return {"message": "❌ مشاور انتخابی معتبر نیست.", "next_state": None}
            
            flow_data["consultant_id"] = callback_data
            flow_data["consultant_name"] = consultant_info["name"]
            context.user_data["flow_data"] = flow_data
            context.user_data["current_step"] = "get_name"
            
            return {
                "message": (
                    f"✅ مشاور انتخاب شده:\n"
                    f"{consultant_info['name']}\n\n"
                    f"👤 لطفا نام خود را وارد کنید:"
                ),
                "next_state": "waiting_name"
            }
        
        return {"message": "لطفا دوباره تلاش کنید.", "next_state": None}
    
    async def process_input(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user_input: str
    ) -> Dict[str, Any]:
        """Process user input in consultation flow."""
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
            context.user_data["current_step"] = None
            context.user_data["flow_state"] = None
            
            # Save booking to database
            from datetime import datetime
            from shared.utils.tracking_code import generate_tracking_code
            from infrastructure.database.repositories.consultation_booking_repository import ConsultationBookingRepository
            import uuid
            
            user = update.effective_user
            tracking_code = generate_tracking_code(5)
            
            booking_repo = ConsultationBookingRepository()
            booking_data = {
                'id': str(uuid.uuid4()),
                'user_id': user.id if user else 0,
                'user_name': flow_data.get('user_name', user.first_name if user else 'نامشخص'),
                'user_contact': flow_data.get('user_contact', 'نامشخص'),
                'consultant_id': flow_data.get('consultant_id'),
                'consultant_name': flow_data.get('consultant_name'),
                'tracking_code': tracking_code,
                'created_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            booking_repo.save(booking_data)
            flow_data['tracking_code'] = tracking_code
            
            completion_msg = (
                f"✅ درخواست مشاوره شما با موفقیت ثبت شد!\n\n"
                f"📋 خلاصه درخواست:\n"
                f"• مشاور: {flow_data.get('consultant_name', 'نامشخص')}\n"
                f"• تماس شما: {flow_data.get('user_contact', 'نامشخص')}\n"
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

