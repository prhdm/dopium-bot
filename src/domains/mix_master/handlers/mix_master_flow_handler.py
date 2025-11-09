"""Mix and Master flow handler."""
from typing import Dict, Any
from telegram import Update
from telegram.ext import ContextTypes


class MixMasterFlowHandler:
    """Handler for mix and master service flow."""
    
    async def start_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
        """Start the mix and master service flow."""
        context.user_data["flow_state"] = "mix_master"
        context.user_data["flow_data"] = {}
        context.user_data["current_step"] = "track_count"
        
        return {
            "message": "🎚️ سرویس میکس و مستر\n\nتعداد ترک‌های پروژه خود را وارد کنید:",
            "next_state": "waiting_track_count"
        }
    
    async def process_input(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user_input: str
    ) -> Dict[str, Any]:
        """Process user input in mix and master flow."""
        current_step = context.user_data.get("current_step")
        flow_data = context.user_data.get("flow_data", {})
        
        if current_step == "track_count":
            flow_data["track_count"] = user_input
            context.user_data["flow_data"] = flow_data
            context.user_data["current_step"] = "format"
            return {
                "message": "💿 فرمت خروجی مورد نظر را مشخص کنید (مثلا: WAV، MP3):",
                "next_state": "waiting_format"
            }
        
        elif current_step == "format":
            flow_data["format"] = user_input
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
                f"✅ درخواست میکس و مستر شما با موفقیت ثبت شد!\n\n"
                f"📋 خلاصه درخواست:\n"
                f"• تعداد ترک: {flow_data.get('track_count', 'نامشخص')}\n"
                f"• فرمت: {flow_data.get('format', 'نامشخص')}\n"
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

