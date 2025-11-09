"""SQLite database connection and setup."""
import sqlite3
import os
from pathlib import Path
from typing import Optional
from config import Settings
import logging

logger = logging.getLogger(__name__)


class SQLiteConnection:
    """SQLite database connection manager."""
    
    _instance: Optional['SQLiteConnection'] = None
    _connection: Optional[sqlite3.Connection] = None
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize SQLite connection.
        
        Args:
            db_path: Path to database file. If None, uses default location.
        """
        if db_path:
            self.db_path = db_path
        else:
            # Default database location: project_root/data/dopium.db
            project_root = Path(__file__).parent.parent.parent.parent
            data_dir = project_root / "data"
            data_dir.mkdir(exist_ok=True)
            self.db_path = str(data_dir / "dopium.db")
        
        self._connection = None
        logger.info(f"SQLite database will be at: {self.db_path}")
    
    def get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False  # Allow connection to be used across threads
            )
            self._connection.row_factory = sqlite3.Row  # Return rows as dict-like objects
            logger.info(f"Connected to SQLite database: {self.db_path}")
        return self._connection
    
    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("SQLite connection closed")
    
    def initialize_schema(self) -> None:
        """Initialize database schema (create tables)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create bookings table for recording domain
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recording_bookings (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                user_contact TEXT NOT NULL,
                service_tier_id TEXT,
                service_option_id TEXT,
                tracking_code TEXT,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                updated_at TEXT
            )
        """)
        
        # Add tracking_code column if it doesn't exist (for existing databases)
        try:
            cursor.execute("ALTER TABLE recording_bookings ADD COLUMN tracking_code TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass
        
        # Create bookings table for music production domain
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS music_production_bookings (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                user_contact TEXT NOT NULL,
                service_tier_id TEXT NOT NULL,
                service_option_id TEXT NOT NULL,
                tracking_code TEXT,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                updated_at TEXT
            )
        """)
        
        # Add tracking_code column if it doesn't exist (for existing databases)
        try:
            cursor.execute("ALTER TABLE music_production_bookings ADD COLUMN tracking_code TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass
        
        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recording_bookings_user_id 
            ON recording_bookings(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recording_bookings_status 
            ON recording_bookings(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_music_production_bookings_user_id 
            ON music_production_bookings(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_music_production_bookings_status 
            ON music_production_bookings(status)
        """)
        
        conn.commit()
        logger.info("Database schema initialized")
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """Execute a SELECT query and return results."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> None:
        """Execute an INSERT/UPDATE/DELETE query."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()


# Singleton instance
_db_instance: Optional[SQLiteConnection] = None


def get_db_connection() -> SQLiteConnection:
    """Get or create singleton database connection."""
    global _db_instance
    if _db_instance is None:
        _db_instance = SQLiteConnection()
        _db_instance.initialize_schema()
    return _db_instance

