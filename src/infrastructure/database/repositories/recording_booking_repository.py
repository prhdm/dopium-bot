"""Recording booking repository implementation using SQLite."""
from datetime import datetime
from typing import Optional
from domains.recording.entities.booking import Booking, BookingId
from infrastructure.database.sqlite_connection import get_db_connection


class RecordingBookingRepository:
    """SQLite implementation of booking repository for recording domain."""
    
    def __init__(self):
        """Initialize repository with database connection."""
        self._db = get_db_connection()
    
    def save(self, booking: Booking) -> Booking:
        """
        Save or update a booking.
        
        Args:
            booking: Booking entity to save
            
        Returns:
            Saved booking entity
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        # Check if booking exists
        cursor.execute("""
            SELECT id FROM recording_bookings WHERE id = ?
        """, (booking.id.value,))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing booking
            cursor.execute("""
                UPDATE recording_bookings
                SET user_name = ?,
                    user_contact = ?,
                    service_tier_id = ?,
                    service_option_id = ?,
                    tracking_code = ?,
                    status = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                booking.user_name,
                booking.user_contact,
                booking.service_tier_id,
                booking.service_option_id,
                booking.tracking_code,
                booking.status,
                datetime.now().isoformat(),
                booking.id.value
            ))
        else:
            # Insert new booking
            cursor.execute("""
                INSERT INTO recording_bookings 
                (id, user_id, user_name, user_contact, service_tier_id, 
                 service_option_id, tracking_code, created_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                booking.id.value,
                booking.user_id,
                booking.user_name,
                booking.user_contact,
                booking.service_tier_id,
                booking.service_option_id,
                booking.tracking_code,
                booking.created_at.isoformat(),
                booking.status
            ))
        
        conn.commit()
        return booking
    
    def find_by_id(self, booking_id: BookingId) -> Optional[Booking]:
        """
        Find booking by ID.
        
        Args:
            booking_id: Booking ID
            
        Returns:
            Booking entity or None if not found
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, user_name, user_contact, service_tier_id,
                   service_option_id, tracking_code, created_at, status
            FROM recording_bookings
            WHERE id = ?
        """, (booking_id.value,))
        
        row = cursor.fetchone()
        
        if row:
            return self._row_to_booking(row)
        return None
    
    def find_by_user_id(self, user_id: int) -> list[Booking]:
        """
        Find all bookings for a user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            List of booking entities
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, user_name, user_contact, service_tier_id,
                   service_option_id, tracking_code, created_at, status
            FROM recording_bookings
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        return [self._row_to_booking(row) for row in rows]
    
    def find_by_status(self, status: str) -> list[Booking]:
        """
        Find bookings by status.
        
        Args:
            status: Booking status (pending, confirmed, cancelled)
            
        Returns:
            List of booking entities
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, user_name, user_contact, service_tier_id,
                   service_option_id, tracking_code, created_at, status
            FROM recording_bookings
            WHERE status = ?
            ORDER BY created_at DESC
        """, (status,))
        
        rows = cursor.fetchall()
        return [self._row_to_booking(row) for row in rows]
    
    def _row_to_booking(self, row) -> Booking:
        """Convert database row to Booking entity."""
        return Booking(
            id=BookingId(row['id']),
            user_id=row['user_id'],
            user_name=row['user_name'],
            user_contact=row['user_contact'],
            created_at=datetime.fromisoformat(row['created_at']),
            service_tier_id=row['service_tier_id'],
            service_option_id=row['service_option_id'],
            tracking_code=row['tracking_code'],
            status=row['status']
        )

