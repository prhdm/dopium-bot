"""Bot application setup."""
import logging
from telegram.ext import Application
from config import Settings
from core.lifecycle import get_post_init_callback

logger = logging.getLogger(__name__)


def create_application() -> Application:
    """
    Create and configure the Telegram bot application.
    
    Returns:
        Application: Configured bot application instance.
    """
    Settings.validate()
    
    application = (
        Application.builder()
        .token(Settings.BOT_TOKEN)
        .post_init(get_post_init_callback())
        .build()
    )
    
    logger.info("Bot application created successfully")
    return application

