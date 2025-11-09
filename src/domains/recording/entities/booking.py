"""Booking entity - Booking domain model."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class BookingId:
    """Booking ID value object."""
    value: str
    
    def __str__(self) -> str:
        return self.value


@dataclass
class Booking:
    """
    Booking entity - Aggregate root.
    
    Represents a booking for recording service.
    """
    
    id: BookingId
    user_id: int
    user_name: str
    user_contact: str
    created_at: datetime
    service_tier_id: Optional[str] = None
    service_option_id: Optional[str] = None
    tracking_code: Optional[str] = None  # کد رهگیری
    status: str = "pending"  # pending, confirmed, cancelled
    
    def __post_init__(self) -> None:
        """Validate booking data."""
        if not self.status or self.status not in ('pending', 'confirmed', 'cancelled'):
            raise ValueError("Invalid booking status")
        if not self.user_name or not self.user_name.strip():
            raise ValueError("User name cannot be empty")
        if not self.user_contact or not self.user_contact.strip():
            raise ValueError("User contact cannot be empty")
    
    def confirm(self) -> None:
        """Confirm the booking."""
        if self.status != "pending":
            raise ValueError("Only pending bookings can be confirmed")
        object.__setattr__(self, 'status', "confirmed")
    
    def cancel(self) -> None:
        """Cancel the booking."""
        if self.status == "cancelled":
            raise ValueError("Booking is already cancelled")
        object.__setattr__(self, 'status', "cancelled")
    
    def is_pending(self) -> bool:
        """Check if booking is pending."""
        return self.status == "pending"
    
    def __eq__(self, other: object) -> bool:
        """Bookings are equal if they have the same ID."""
        if not isinstance(other, Booking):
            return False
        return self.id.value == other.id.value
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id.value)

