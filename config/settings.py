"""Application settings and configuration."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Bot Configuration
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
    GROUP_ID: str = os.getenv('GROUP_ID', '')
    CHANNEL_ID: str = os.getenv('CHANNEL_ID', '')
    CHANNEL_USERNAME: str = os.getenv('CHANNEL_USERNAME', '')
    
    @classmethod
    def validate(cls) -> None:
        """Validate required settings."""
        if not cls.BOT_TOKEN:
            raise ValueError(
                "BOT_TOKEN environment variable is required. "
                "Please set it in .env file."
            )
    
    @classmethod
    def get_group_id(cls) -> str | None:
        """Get group ID if set, otherwise return None."""
        return cls.GROUP_ID if cls.GROUP_ID else None
    
    @classmethod
    def get_channel_id(cls) -> str | None:
        """Get channel ID if set, otherwise return None."""
        return cls.CHANNEL_ID if cls.CHANNEL_ID else None
    
    @classmethod
    def get_channel_username(cls) -> str | None:
        """Get channel username if set, otherwise return None."""
        return cls.CHANNEL_USERNAME if cls.CHANNEL_USERNAME else None
    
    @classmethod
    def get_channel_identifier(cls) -> str | None:
        """Get channel identifier (username or ID) for join button."""
        if cls.CHANNEL_USERNAME:
            # Remove @ if present
            username = cls.CHANNEL_USERNAME.replace('@', '')
            return f"@{username}"
        return cls.CHANNEL_ID if cls.CHANNEL_ID else None
    
    @classmethod
    def get_channel_identifier_for_validation(cls) -> str | None:
        """Get channel identifier for membership validation (username or ID)."""
        # Prefer username for validation
        if cls.CHANNEL_USERNAME:
            username = cls.CHANNEL_USERNAME.replace('@', '')
            return username
        return cls.CHANNEL_ID if cls.CHANNEL_ID else None

