"""Mix and Master flow handler."""
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import Settings


class MixMasterFlowHandler:
    """Handler for mix and master service flow."""
    
    async def start_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
        """Start the mix and master service flow."""
        context.user_data["flow_state"] = "mix_master"
        context.user_data["flow_data"] = {}
        context.user_data["current_step"] = "select_plan"
        
        # Create inline keyboard with three plans
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "هنرجویان میکس مجموعه - 3 تومن",
                callback_data="plan_students"
            )],
            [InlineKeyboardButton(
                "میکس‌من های مجموعه - 4.5 تومن",
                callback_data="plan_mixers"
            )],
            [InlineKeyboardButton(
                "پریمیوم (نظارت + تغییرات) - 8 تومن",
                callback_data="plan_premium"
            )]
        ])
        
        return {
            "message": (
                "🎛 میکس و مستر\n\n"
                "برای میکس و مسترینگ یک پروژه توی دوپیوم سه تا پلن داریم که میتونید به نسبت کاری که بستید و شرایطتتون یکیش رو انتخاب کنید:\n\n"
            ),
            "keyboard": keyboard,
            "next_state": "waiting_plan_selection"
        }
    
    async def process_callback(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        callback_data: str
    ) -> Dict[str, Any]:
        """Process callback query (plan selection)."""
        current_step = context.user_data.get("current_step")
        flow_data = context.user_data.get("flow_data", {})
        
        if current_step == "select_plan":
            # Plan selected
            plan_mapping = {
                "plan_students": {
                    "name": "میکس و مسترینگ دیجیتال توسط هنرجویان میکس مجموعه",
                    "price": "3 تومن"
                },
                "plan_mixers": {
                    "name": "میکس و مسترینگ دیجیتال توسط میکس‌من های مجموعه",
                    "price": "4.5 تومن"
                },
                "plan_premium": {
                    "name": "میکس و مسترینگ دیجیتال توسط میکس‌من های مجموعه + نظارت معراج ناجی و عیهود + تغییرات در ضمن کار",
                    "price": "8 تومن"
                }
            }
            
            plan_info = plan_mapping.get(callback_data)
            if not plan_info:
                return {"message": "❌ پلن انتخابی معتبر نیست.", "next_state": None}
            
            flow_data["plan_id"] = callback_data
            flow_data["plan_name"] = plan_info["name"]
            flow_data["plan_price"] = plan_info["price"]
            context.user_data["flow_data"] = flow_data
            context.user_data["current_step"] = "get_name"
            
            return {
                "message": (
                    f"✅ پلن انتخاب شده:\n"
                    f"{plan_info['name']}\n"
                    f"💰 قیمت: {plan_info['price']}\n\n"
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
        """Process user input in mix and master flow."""
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
            from infrastructure.database.repositories.mix_master_booking_repository import MixMasterBookingRepository
            import uuid
            
            user = update.effective_user
            tracking_code = generate_tracking_code(5)
            
            booking_repo = MixMasterBookingRepository()
            booking_data = {
                'id': str(uuid.uuid4()),
                'user_id': user.id if user else 0,
                'user_name': flow_data.get('user_name', user.first_name if user else 'نامشخص'),
                'user_contact': flow_data.get('user_contact', 'نامشخص'),
                'plan_id': flow_data.get('plan_id'),
                'plan_name': flow_data.get('plan_name'),
                'plan_price': flow_data.get('plan_price'),
                'tracking_code': tracking_code,
                'created_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            booking_repo.save(booking_data)
            flow_data['tracking_code'] = tracking_code
            
            # Send notification to group
            await self._send_booking_notification(update, context, flow_data)
            
            completion_msg = (
                f"✅ درخواست میکس و مستر شما با موفقیت ثبت شد!\n\n"
                f"📋 خلاصه درخواست:\n"
                f"• پلن: {flow_data.get('plan_name', 'نامشخص')}\n"
                f"• قیمت: {flow_data.get('plan_price', 'نامشخص')}\n"
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
    
    async def _send_booking_notification(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        flow_data: Dict[str, Any]
    ) -> None:
        """Send booking notification to group."""
        user = update.effective_user
        user_name = flow_data.get('user_name', user.first_name if user else 'نامشخص')
        user_contact = flow_data.get('user_contact', 'نامشخص')
        plan_name = flow_data.get('plan_name', 'نامشخص')
        plan_price = flow_data.get('plan_price', 'نامشخص')
        
        booking_message = (
            f"📋 رزرو جدید - سرویس میکس و مستر\n\n"
            f"👤 کاربر: {user_name}\n"
            f"📞 تماس: {user_contact}\n"
            f"🎚️ پلن: {plan_name}\n"
            f"💰 قیمت: {plan_price}\n"
            f"📊 وضعیت: pending"
        )
        
        # Send to group if configured
        group_id = Settings.get_group_id()
        if group_id:
            try:
                await context.bot.send_message(
                    chat_id=group_id,
                    text=booking_message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"Failed to send mix master notification to group: {e}")

