"""Consultation flow handler."""
from typing import Dict, Any
from telegram import Update
from telegram.ext import ContextTypes


class ConsultationFlowHandler:
    """Handler for consultation service flow."""
    
    async def start_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
        """Start the consultation service flow."""
        context.user_data["flow_state"] = "consultation"
        context.user_data["flow_data"] = {}
        context.user_data["current_step"] = "topic"
        
        return {
            "message": (
                "💡 سرویس مشاوره\n\n"
                "لطفا موضوع مشاوره مورد نظر خود را وارد کنید:\n"
                "مثال: مشاوره تولید موسیقی، راهنمایی استودیو و..."
            ),
            "next_state": "waiting_topic"
        }
    
    async def process_input(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user_input: str
    ) -> Dict[str, Any]:
        """Process user input in consultation flow."""
        current_step = context.user_data.get("current_step")
        flow_data = context.user_data.get("flow_data", {})
        
        if current_step == "topic":
            flow_data["topic"] = user_input
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
                f"✅ درخواست مشاوره شما با موفقیت ثبت شد!\n\n"
                f"📋 خلاصه درخواست:\n"
                f"• موضوع: {flow_data.get('topic', 'نامشخص')}\n"
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

