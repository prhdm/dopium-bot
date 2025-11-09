"""Complete booking use case."""
from datetime import datetime
from uuid import uuid4
from domains.music_production.repositories import IMusicProductionRepository
from domains.music_production.dto import BookingRequestDTO, BookingResponseDTO
from domains.music_production.entities.booking import Booking, BookingId
import sys
from pathlib import Path

# Add src to path for infrastructure imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from infrastructure.database.repositories.music_production_booking_repository import MusicProductionBookingRepository
from shared.utils.tracking_code import generate_tracking_code


class CompleteBookingUseCase:
    """Use case to complete a booking."""
    
    def __init__(self, repository: IMusicProductionRepository):
        """Initialize use case."""
        self._repository = repository
        self._booking_repository = MusicProductionBookingRepository()
    
    def execute(self, request: BookingRequestDTO) -> BookingResponseDTO:
        """
        Execute use case - complete booking.
        
        Args:
            request: Booking request DTO
            
        Returns:
            BookingResponseDTO
            
        Raises:
            ValueError: If tier or option not found
        """
        tier = self._repository.get_service_tier_by_id(request.service_tier_id)
        if not tier:
            raise ValueError(f"Service tier with ID {request.service_tier_id} not found")
        
        option = self._repository.get_service_option_by_id(request.service_option_id)
        if not option:
            raise ValueError(f"Service option with ID {request.service_option_id} not found")
        
        # Generate tracking code
        tracking_code = generate_tracking_code(5)
        
        booking = Booking(
            id=BookingId(str(uuid4())),
            user_id=request.user_id,
            user_name=request.user_name,
            user_contact=request.user_contact,
            service_tier_id=request.service_tier_id,
            service_option_id=request.service_option_id,
            tracking_code=tracking_code,
            created_at=datetime.now(),
            status="pending"
        )
        
        saved_booking = self._booking_repository.save(booking)
        
        return BookingResponseDTO(
            booking_id=saved_booking.id.value,
            user_name=saved_booking.user_name,
            user_contact=saved_booking.user_contact,
            service_tier_name=tier.name,
            service_option_name=option.name,
            service_option_price=option.price,
            tracking_code=saved_booking.tracking_code or tracking_code,
            status=saved_booking.status
        )

