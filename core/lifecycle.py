"""Application lifecycle hooks."""
import logging
from telegram.ext import Application
from config import Settings

logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """
    Send welcome message to the group when bot starts.
    
    Args:
        application: The bot application instance.
    """
    group_id = Settings.get_group_id()
    
    if not group_id:
        logger.warning("GROUP_ID not set, skipping welcome message")
        return
    
    try:
        # await application.bot.send_message(
        #     chat_id=group_id,
        #     text="🤖 Bot is now online and ready to assist! 👋"
        # )
        logger.info(f"Welcome message sent to group {group_id}")
    except Exception as e:
        logger.error(f"Failed to send welcome message to group: {e}")


def get_post_init_callback():
    """
    Get the post_init callback function.
    
    Returns:
        Callable: The post_init callback function.
    """
    return post_init

