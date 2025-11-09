"""Distribution flow handler."""
from typing import Dict, Any
from telegram import Update
from telegram.ext import ContextTypes


class DistributionFlowHandler:
    """Handler for distribution service flow."""
    
    async def start_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
        """Start the distribution service flow."""
        context.user_data["flow_state"] = "distribution"
        context.user_data["flow_data"] = {}
        context.user_data["current_step"] = "platforms"
        
        return {
            "message": (
                "📦 سرویس دیستریبیوشن\n\n"
                "پلتفرم‌های مورد نظر برای انتشار را مشخص کنید:\n"
                "مثال: Spotify، Apple Music، YouTube Music و..."
            ),
            "next_state": "waiting_platforms"
        }
    
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
            
            completion_msg = (
                f"✅ درخواست دیستریبیوشن شما با موفقیت ثبت شد!\n\n"
                f"📋 خلاصه درخواست:\n"
                f"• پلتفرم‌ها: {flow_data.get('platforms', 'نامشخص')}\n"
                f"• تاریخ انتشار: {flow_data.get('release_date', 'نامشخص')}\n"
                f"• اطلاعات تماس: {flow_data.get('contact_info', 'نامشخص')}\n\n"
                f"📞 به زودی با شما تماس گرفته خواهد شد."
            )
            
            return {
                "message": completion_msg,
                "next_state": "completed",
                "completed": True,
                "restore_keyboard": True
            }
        
        return {"message": "لطفا دوباره تلاش کنید.", "next_state": None}

