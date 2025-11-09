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
        
        # Create bookings table for mix_master domain
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mix_master_bookings (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                user_contact TEXT NOT NULL,
                plan_id TEXT,
                plan_name TEXT,
                plan_price TEXT,
                tracking_code TEXT,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                updated_at TEXT
            )
        """)
        
        # Create bookings table for consultation domain
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consultation_bookings (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                user_contact TEXT NOT NULL,
                consultant_id TEXT,
                consultant_name TEXT,
                tracking_code TEXT,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                updated_at TEXT
            )
        """)
        
        # Create bookings table for distribution domain
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS distribution_bookings (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                user_contact TEXT NOT NULL,
                pricing_id TEXT,
                pricing_name TEXT,
                pricing_price TEXT,
                platforms TEXT,
                release_date TEXT,
                tracking_code TEXT,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                updated_at TEXT
            )
        """)
        
        # Add pricing columns if they don't exist (for existing databases)
        try:
            cursor.execute("ALTER TABLE distribution_bookings ADD COLUMN pricing_id TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE distribution_bookings ADD COLUMN pricing_name TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE distribution_bookings ADD COLUMN pricing_price TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_mix_master_bookings_user_id 
            ON mix_master_bookings(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_mix_master_bookings_status 
            ON mix_master_bookings(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_consultation_bookings_user_id 
            ON consultation_bookings(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_consultation_bookings_status 
            ON consultation_bookings(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_distribution_bookings_user_id 
            ON distribution_bookings(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_distribution_bookings_status 
            ON distribution_bookings(status)
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

