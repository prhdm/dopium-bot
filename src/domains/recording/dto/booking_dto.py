"""Booking DTOs."""
from dataclasses import dataclass


@dataclass
class BookingRequestDTO:
    """Request DTO for creating a booking."""
    
    user_id: int
    user_name: str
    user_contact: str
    service_tier_id: str  # "basic" or "premium"
    service_option_id: str  # Selected option ID


@dataclass
class BookingResponseDTO:
    """Response DTO for booking operations."""
    
    booking_id: str
    user_name: str
    user_contact: str
    service_tier_name: str
    service_option_name: str
    service_option_price: str
    is_hourly: bool
    tracking_code: str  # کد رهگیری
    status: str
    
    def to_message(self) -> str:
        """Convert to formatted message for group notification."""
        price_display = f"ساعتی {self.service_option_price}" if self.is_hourly else self.service_option_price
        return (
            f"📋 رزرو جدید - سرویس ضبط\n\n"
            f"👤 کاربر: {self.user_name}\n"
            f"📞 تماس: {self.user_contact}\n"
            f"🎚️ پلن: {self.service_tier_name}\n"
            f"🎙️ سرویس: {self.service_option_name}\n"
            f"💰 قیمت: {price_display}\n"
            f"🔖 کد رهگیری: `{self.tracking_code}`\n"
            f"📊 وضعیت: {self.status}"
        )

