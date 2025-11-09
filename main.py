import logging
import sys
from pathlib import Path
from telegram import Update
from core import create_application
from handlers import register_command_handlers, register_message_handlers, register_keyboard_handlers

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from shared.handlers.flow_manager import FlowManager
from domains.recording import (
    RecordingRepository,
    GetServiceTiersUseCase,
    GetServiceTierOptionsUseCase,
    CompleteBookingUseCase,
    RecordingFlowHandler,
)
from domains.music_production import (
    MusicProductionRepository,
    GetServiceTiersUseCase as MPGetServiceTiersUseCase,
    GetServiceTierOptionsUseCase as MPGetServiceTierOptionsUseCase,
    CompleteBookingUseCase as MPCompleteBookingUseCase,
    MusicProductionFlowHandler,
)
from domains.mix_master import MixMasterFlowHandler
from domains.consultation import ConsultationFlowHandler
from domains.distribution import DistributionFlowHandler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def initialize_domain_handlers():
    """Initialize and register domain handlers with FlowManager."""
    # Import here to avoid circular imports
    from handlers.keyboard import create_reply_keyboard, create_cancel_keyboard
    
    # Set the keyboard creators
    FlowManager.set_reply_keyboard_creator(create_reply_keyboard)
    FlowManager.set_cancel_keyboard_creator(create_cancel_keyboard)
    
    # Recording domain
    recording_repo = RecordingRepository()
    recording_get_tiers = GetServiceTiersUseCase(recording_repo)
    recording_get_options = GetServiceTierOptionsUseCase(recording_repo)
    recording_complete = CompleteBookingUseCase(recording_repo)
    recording_handler = RecordingFlowHandler(
        recording_get_tiers,
        recording_get_options,
        recording_complete
    )
    FlowManager.register_handler("recording", recording_handler)
    
    # Music Production domain
    mp_repo = MusicProductionRepository()
    mp_get_tiers = MPGetServiceTiersUseCase(mp_repo)
    mp_get_options = MPGetServiceTierOptionsUseCase(mp_repo)
    mp_complete = MPCompleteBookingUseCase(mp_repo)
    mp_handler = MusicProductionFlowHandler(
        mp_get_tiers,
        mp_get_options,
        mp_complete
    )
    FlowManager.register_handler("music_production", mp_handler)
    
    # Mix Master domain
    mix_master_handler = MixMasterFlowHandler()
    FlowManager.register_handler("mix_master", mix_master_handler)
    
    # Consultation domain
    consultation_handler = ConsultationFlowHandler()
    FlowManager.register_handler("consultation", consultation_handler)
    
    # Distribution domain
    distribution_handler = DistributionFlowHandler()
    FlowManager.register_handler("distribution", distribution_handler)


def main() -> None:
    """Initialize and start the bot."""
    try:
        # Initialize database connection
        from infrastructure.database.sqlite_connection import get_db_connection
        db = get_db_connection()
        logger.info("Database initialized successfully")
        
        # Initialize domain handlers
        initialize_domain_handlers()
        
        # Create application (lifecycle hooks are setup in create_application)
        application = create_application()
        
        # Register handlers
        register_command_handlers(application)
        register_message_handlers(application)
        register_keyboard_handlers(application)
        
        # Start the bot
        logger.info("Bot is starting...")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True  # Drop pending updates to avoid conflicts
        )
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        error_msg = str(e)
        if "Conflict" in error_msg or "terminated by other getUpdates" in error_msg:
            logger.error(
                "❌ Bot conflict detected! Another bot instance is already running.\n"
                "Please:\n"
                "1. Stop the other bot instance, OR\n"
                "2. Wait a few seconds and try again, OR\n"
                "3. Use drop_pending_updates=True (already enabled)"
            )
        else:
            logger.error(f"Bot crashed with error: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()

