"""Booking DTOs."""
from dataclasses import dataclass


@dataclass
class BookingRequestDTO:
    """Request DTO for creating a booking."""
    
    user_id: int
    user_name: str
    user_contact: str
    service_tier_id: str
    service_option_id: str


@dataclass
class BookingResponseDTO:
    """Response DTO for booking operations."""
    
    booking_id: str
    user_name: str
    user_contact: str
    service_tier_name: str
    service_option_name: str
    service_option_price: str
    tracking_code: str  # کد رهگیری
    status: str
    
    def to_message(self) -> str:
        """Convert to formatted message for group notification."""
        return (
            f"📋 رزرو جدید - سرویس آهنگسازی\n\n"
            f"👤 کاربر: {self.user_name}\n"
            f"📞 تماس: {self.user_contact}\n"
            f"🎚️ پلن: {self.service_tier_name}\n"
            f"🎵 سرویس: {self.service_option_name}\n"
            f"💰 قیمت: {self.service_option_price}\n"
            f"🔖 کد رهگیری: `{self.tracking_code}`\n"
            f"📊 وضعیت: {self.status}"
        )

