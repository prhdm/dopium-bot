"""Complete booking use case."""
from datetime import datetime
from uuid import uuid4
from domains.recording.repositories import IRecordingRepository
from domains.recording.dto import BookingRequestDTO, BookingResponseDTO
from domains.recording.entities import Booking
from domains.recording.entities.booking import BookingId
import sys
from pathlib import Path

# Add src to path for infrastructure imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from infrastructure.database.repositories.recording_booking_repository import RecordingBookingRepository
from shared.utils.tracking_code import generate_tracking_code


class CompleteBookingUseCase:
    """
    Use case to complete a booking.
    
    Single Responsibility: Create and persist booking.
    """
    
    def __init__(self, recording_repository: IRecordingRepository):
        """Initialize use case with repository."""
        self._recording_repository = recording_repository
        self._booking_repository = RecordingBookingRepository()
    
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
        # Validate tier exists
        tier = self._recording_repository.get_service_tier_by_id(request.service_tier_id)
        if not tier:
            raise ValueError(f"Service tier with ID {request.service_tier_id} not found")
        
        # Validate option exists
        option = self._recording_repository.get_service_option_by_id(request.service_option_id)
        if not option:
            raise ValueError(f"Service option with ID {request.service_option_id} not found")
        
        # Generate tracking code
        tracking_code = generate_tracking_code(5)
        
        # Create booking entity
        booking = Booking(
            id=BookingId(str(uuid4())),
            user_id=request.user_id,
            user_name=request.user_name,
            user_contact=request.user_contact,
            created_at=datetime.now(),
            service_tier_id=request.service_tier_id,
            service_option_id=request.service_option_id,
            tracking_code=tracking_code,
            status="pending"
        )
        
        # Persist booking to database
        saved_booking = self._booking_repository.save(booking)
        
        # Return response DTO
        return BookingResponseDTO(
            booking_id=saved_booking.id.value,
            user_name=saved_booking.user_name,
            user_contact=saved_booking.user_contact,
            service_tier_name=tier.name,
            service_option_name=option.name,
            service_option_price=option.price,
            is_hourly=option.is_hourly,
            tracking_code=saved_booking.tracking_code or tracking_code,
            status=saved_booking.status
        )

