"""Music production booking repository implementation using SQLite."""
from datetime import datetime
from typing import Optional
from domains.music_production.entities.booking import Booking, BookingId
from infrastructure.database.sqlite_connection import get_db_connection


class MusicProductionBookingRepository:
    """SQLite implementation of booking repository for music production domain."""
    
    def __init__(self):
        """Initialize repository with database connection."""
        self._db = get_db_connection()
    
    def save(self, booking: Booking) -> Booking:
        """Save or update a booking."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM music_production_bookings WHERE id = ?
        """, (booking.id.value,))
        
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE music_production_bookings
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
            cursor.execute("""
                INSERT INTO music_production_bookings 
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
        """Find booking by ID."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, user_name, user_contact, service_tier_id,
                   service_option_id, tracking_code, created_at, status
            FROM music_production_bookings
            WHERE id = ?
        """, (booking_id.value,))
        
        row = cursor.fetchone()
        
        if row:
            return self._row_to_booking(row)
        return None
    
    def find_by_user_id(self, user_id: int) -> list[Booking]:
        """Find all bookings for a user."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, user_name, user_contact, service_tier_id,
                   service_option_id, tracking_code, created_at, status
            FROM music_production_bookings
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
            FROM music_production_bookings
            WHERE status = ?
            ORDER BY created_at DESC
        """, (status,))
        
        rows = cursor.fetchall()
        return [self._row_to_booking(row) for row in rows]
    
    def find_by_tracking_code(self, tracking_code: str) -> Optional[Booking]:
        """
        Find booking by tracking code.
        
        Args:
            tracking_code: Tracking code
            
        Returns:
            Booking entity or None if not found
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, user_name, user_contact, service_tier_id,
                   service_option_id, tracking_code, created_at, status
            FROM music_production_bookings
            WHERE tracking_code = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (tracking_code,))
        
        row = cursor.fetchone()
        if row:
            return self._row_to_booking(row)
        return None
    
    def find_all(self) -> list[Booking]:
        """
        Find all bookings regardless of status.
        
        Returns:
            List of all booking entities, sorted by created_at DESC (newest first)
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, user_name, user_contact, service_tier_id,
                   service_option_id, tracking_code, created_at, status
            FROM music_production_bookings
            ORDER BY created_at DESC
        """)
        
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

