"""Admin repository for managing admin users."""
from infrastructure.database.sqlite_connection import get_db_connection
import logging

logger = logging.getLogger(__name__)


class AdminRepository:
    """Repository for admin user management."""
    
    def __init__(self):
        """Initialize repository with database connection."""
        self._db = get_db_connection()
        self._initialize_table()
    
    def _initialize_table(self):
        """Initialize admin users table."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                created_at TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_admin_users_user_id 
            ON admin_users(user_id)
        """)
        
        conn.commit()
        logger.info("Admin users table initialized")
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is an admin."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id FROM admin_users 
            WHERE user_id = ? AND is_active = 1
        """, (user_id,))
        
        return cursor.fetchone() is not None
    
    def add_admin(self, user_id: int, username: str = None, full_name: str = None) -> bool:
        """Add a new admin user."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        from datetime import datetime
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO admin_users 
                (user_id, username, full_name, created_at, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, (user_id, username, full_name, datetime.now().isoformat()))
            
            conn.commit()
            logger.info(f"Admin user added: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding admin: {e}")
            return False
    
    def remove_admin(self, user_id: int) -> bool:
        """Remove admin (set inactive)."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE admin_users SET is_active = 0 WHERE user_id = ?
            """, (user_id,))
            
            conn.commit()
            logger.info(f"Admin user removed: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing admin: {e}")
            return False
    
    def get_all_admins(self) -> list:
        """Get all active admin users."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, username, full_name, created_at
            FROM admin_users
            WHERE is_active = 1
            ORDER BY created_at DESC
        """)
        
        return cursor.fetchall()




