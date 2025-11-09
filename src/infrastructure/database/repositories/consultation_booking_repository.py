"""Consultation booking repository implementation using SQLite."""
from datetime import datetime
from typing import Optional
from infrastructure.database.sqlite_connection import get_db_connection
import uuid


class ConsultationBookingRepository:
    """SQLite implementation of booking repository for consultation domain."""
    
    def __init__(self):
        """Initialize repository with database connection."""
        self._db = get_db_connection()
    
    def save(self, booking_data: dict) -> dict:
        """Save a consultation booking."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        booking_id = booking_data.get('id', str(uuid.uuid4()))
        
        cursor.execute("""
            SELECT id FROM consultation_bookings WHERE id = ?
        """, (booking_id,))
        
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE consultation_bookings
                SET user_name = ?,
                    user_contact = ?,
                    consultant_id = ?,
                    consultant_name = ?,
                    tracking_code = ?,
                    status = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                booking_data['user_name'],
                booking_data['user_contact'],
                booking_data.get('consultant_id'),
                booking_data.get('consultant_name'),
                booking_data.get('tracking_code'),
                booking_data.get('status', 'pending'),
                datetime.now().isoformat(),
                booking_id
            ))
        else:
            cursor.execute("""
                INSERT INTO consultation_bookings 
                (id, user_id, user_name, user_contact, consultant_id, consultant_name, tracking_code, created_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                booking_id,
                booking_data['user_id'],
                booking_data['user_name'],
                booking_data['user_contact'],
                booking_data.get('consultant_id'),
                booking_data.get('consultant_name'),
                booking_data.get('tracking_code'),
                booking_data.get('created_at', datetime.now().isoformat()),
                booking_data.get('status', 'pending')
            ))
        
        conn.commit()
        booking_data['id'] = booking_id
        return booking_data
    
    def find_all(self) -> list:
        """Find all consultation bookings, sorted by created_at DESC."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, user_name, user_contact, consultant_id, consultant_name,
                   tracking_code, created_at, status
            FROM consultation_bookings
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def find_by_tracking_code(self, tracking_code: str) -> Optional[dict]:
        """Find booking by tracking code."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, user_name, user_contact, consultant_id, consultant_name,
                   tracking_code, created_at, status
            FROM consultation_bookings
            WHERE tracking_code = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (tracking_code,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def find_by_status(self, status: str) -> list:
        """Find bookings by status."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, user_name, user_contact, consultant_id, consultant_name,
                   tracking_code, created_at, status
            FROM consultation_bookings
            WHERE status = ?
            ORDER BY created_at DESC
        """, (status,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def find_by_id(self, booking_id: str) -> Optional[dict]:
        """Find booking by ID."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, user_name, user_contact, consultant_id, consultant_name,
                   tracking_code, created_at, status
            FROM consultation_bookings
            WHERE id = ?
        """, (booking_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

