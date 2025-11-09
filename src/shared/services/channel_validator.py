"""Channel membership validator - Shared service interface and implementation."""
from abc import ABC, abstractmethod
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import Settings
import logging

logger = logging.getLogger(__name__)


class IChannelMembershipValidator(ABC):
    """Interface for channel membership validation."""
    
    @abstractmethod
    async def check_membership(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check if user is a member of the required channel."""
        pass
    
    @abstractmethod
    def create_join_button(self) -> Optional[InlineKeyboardMarkup]:
        """Create inline keyboard with channel join button."""
        pass
    
    @abstractmethod
    async def send_join_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        message_id: Optional[int] = None
    ) -> None:
        """Send join channel message with button."""
        pass


class ChannelMembershipValidator(IChannelMembershipValidator):
    """Implementation of channel membership validator."""
    
    @staticmethod
    async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check if user is a member of the channel."""
        channel_identifier = Settings.get_channel_identifier_for_validation()
        
        if not channel_identifier:
            logger.info("No channel identifier configured, skipping membership check")
            return True
        
        user = update.effective_user
        if not user:
            logger.warning("No user in update, cannot check membership")
            return False
        
        # Try different formats for channel identifier
        identifiers_to_try = []
        
        # If it's a username (without @), try both with and without @
        if not channel_identifier.startswith('-') and not channel_identifier.startswith('@'):
            identifiers_to_try.append(f"@{channel_identifier}")
            identifiers_to_try.append(channel_identifier)
        else:
            identifiers_to_try.append(channel_identifier)
        
        # Also try numeric ID if we have a username
        channel_id = Settings.get_channel_id()
        if channel_id and channel_id not in identifiers_to_try:
            identifiers_to_try.append(channel_id)
        
        for chat_id in identifiers_to_try:
            try:
                logger.info(f"Checking membership for user {user.id} in channel: {chat_id}")
                member = await context.bot.get_chat_member(
                    chat_id=chat_id,
                    user_id=user.id
                )
                
                valid_statuses = ['member', 'administrator', 'creator']
                is_member = member.status in valid_statuses
                
                logger.info(f"User {user.id} membership check in {chat_id}: status={member.status}, is_member={is_member}")
                
                if is_member:
                    return True
                    
            except Exception as e:
                logger.warning(f"Failed to check membership with identifier '{chat_id}': {e}")
                continue
        
        logger.error(f"Could not verify membership for user {user.id} in channel {channel_identifier}. All attempts failed.")
        
        # Check if bot is admin in the channel (required for membership checks)
        try:
            bot_member = await context.bot.get_chat_member(
                chat_id=identifiers_to_try[0],
                user_id=context.bot.id
            )
            logger.info(f"Bot membership status in channel: {bot_member.status}")
            if bot_member.status not in ['administrator', 'creator', 'member']:
                logger.error("Bot is not a member/admin of the channel! Bot needs to be added as admin to check user memberships.")
        except Exception as bot_error:
            logger.error(f"Could not check bot's own membership: {bot_error}")
        
        # Return False to enforce validation, but log the issue
        # If you want to temporarily allow all users, change this to True
        return False
    
    @staticmethod
    def create_join_button() -> Optional[InlineKeyboardMarkup]:
        """Create inline keyboard with channel join button."""
        channel_username = Settings.get_channel_username()
        channel_id = Settings.get_channel_id()
        
        if not channel_username and not channel_id:
            return None
        
        # Prefer username for URL (more reliable)
        if channel_username:
            username = channel_username.replace('@', '')
            url = f"https://t.me/{username}"
        elif channel_id:
            # For numeric channel ID, try to construct URL
            # Note: This may not work if channel doesn't have public username
            clean_id = channel_id.replace('-100', '')
            url = f"https://t.me/c/{clean_id}"
        else:
            return None
        
        button = InlineKeyboardButton("✅ عضویت در کانال", url=url)
        return InlineKeyboardMarkup([[button]])
    
    @staticmethod
    async def send_join_message(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        message_id: Optional[int] = None
    ) -> None:
        """Send join channel message with button."""
        message_text = "لطفا برای استفاده از خدمات در کانال مجموعه عضو شوید."
        keyboard = ChannelMembershipValidator.create_join_button()
        
        if message_id:
            if update.callback_query:
                await update.callback_query.message.edit_text(
                    message_text,
                    reply_markup=keyboard
                )
            else:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=message_id,
                    text=message_text,
                    reply_markup=keyboard
                )
        else:
            if update.callback_query:
                await update.callback_query.message.reply_text(
                    message_text,
                    reply_markup=keyboard
                )
            elif update.message:
                await update.message.reply_text(
                    message_text,
                    reply_markup=keyboard
                )

