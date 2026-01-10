"""
Telegram Sender Module
Handles sending messages via Telegram Bot API to multiple recipients.
"""

import logging
import asyncio
from typing import List, Dict
from telegram import Bot
from telegram.error import TelegramError
from telegram.constants import ParseMode

from config import Config

# Set up logging
logger = logging.getLogger(__name__)


class TelegramSender:
    """Handles sending messages via Telegram Bot."""
    
    def __init__(self):
        """Initialize the Telegram sender."""
        self.bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        self.chat_ids = [cid.strip() for cid in Config.TELEGRAM_CHAT_IDS if cid.strip()]
        
        if not self.chat_ids:
            logger.warning("No chat IDs configured")
    
    async def send_message_to_chat(self, chat_id: str, message: str) -> Dict:
        """Send a message to a single chat."""
        try:
            logger.info(f"Sending message to chat ID: {chat_id}")
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            
            logger.info(f"Successfully sent message to {chat_id}")
            return {'chat_id': chat_id, 'success': True, 'error': None}
            
        except TelegramError as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            return {'chat_id': chat_id, 'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error sending to {chat_id}: {e}", exc_info=True)
            return {'chat_id': chat_id, 'success': False, 'error': str(e)}
    
    async def send_message_to_all(self, message: str) -> List[Dict]:
        """Send a message to all configured chat IDs."""
        if not self.chat_ids:
            logger.error("No chat IDs configured for sending")
            return []
        
        if Config.TESTING_MODE:
            logger.info("TESTING MODE: Would send to the following chat IDs:")
            for chat_id in self.chat_ids:
                logger.info(f"  - {chat_id}")
            logger.info(f"\nMessage content:\n{message}\n")
            return [{'chat_id': chat_id, 'success': True, 'error': None, 'testing_mode': True} for chat_id in self.chat_ids]
        
        logger.info(f"Sending message to {len(self.chat_ids)} recipients")
        
        results = []
        for i, chat_id in enumerate(self.chat_ids):
            result = await self.send_message_to_chat(chat_id, message)
            results.append(result)
            if i < len(self.chat_ids) - 1:
                await asyncio.sleep(0.5)
        
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        logger.info(f"Message delivery summary: {successful} successful, {failed} failed")
        
        if failed > 0:
            logger.warning("Failed deliveries:")
            for result in results:
                if not result['success']:
                    logger.warning(f"  - {result['chat_id']}: {result['error']}")
        
        return results
    
    async def send_personalized_messages(self, generator) -> List[Dict]:
        """Send personalized messages to each recipient in their preferred language."""
        if not self.chat_ids:
            logger.error("No chat IDs configured for sending")
            return []
        
        logger.info(f"Sending personalized messages to {len(self.chat_ids)} recipients")
        
        results = []
        for i, chat_id in enumerate(self.chat_ids):
            try:
                language = Config.get_language_for_chat(chat_id)
                logger.info(f"Generating message for {chat_id} in {language}")
                
                message = generator.generate_daily_message(language)
                
                if not message:
                    logger.error(f"Failed to generate message for {chat_id}")
                    results.append({'chat_id': chat_id, 'success': False, 'error': 'Message generation failed', 'language': language})
                    continue
                
                if Config.TESTING_MODE:
                    logger.info(f"TESTING MODE: Would send to {chat_id} ({language})")
                    results.append({'chat_id': chat_id, 'success': True, 'error': None, 'language': language, 'testing_mode': True})
                else:
                    result = await self.send_message_to_chat(chat_id, message)
                    result['language'] = language
                    results.append(result)
                    
                    if i < len(self.chat_ids) - 1:
                        await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error sending to {chat_id}: {e}", exc_info=True)
                results.append({'chat_id': chat_id, 'success': False, 'error': str(e)})
        
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        logger.info(f"Personalized message delivery: {successful} successful, {failed} failed")
        
        return results
    
    def send_message_sync(self, message: str) -> List[Dict]:
        """Synchronous wrapper for sending messages."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.send_message_to_all(message))
    
    def send_personalized_messages_sync(self, generator) -> List[Dict]:
        """Synchronous wrapper for sending personalized messages."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.send_personalized_messages(generator))
    
    async def test_connection(self) -> bool:
        """Test the bot connection and validate chat IDs."""
        try:
            logger.info("Testing Telegram bot connection...")
            bot_info = await self.bot.get_me()
            logger.info(f"Bot connected: @{bot_info.username} ({bot_info.first_name})")
            
            if not self.chat_ids:
                logger.warning("No chat IDs to test")
                return False
            
            valid_chats = []
            for chat_id in self.chat_ids:
                try:
                    chat = await self.bot.get_chat(chat_id)
                    logger.info(f"Chat ID {chat_id} is valid: {chat.type}")
                    valid_chats.append(chat_id)
                except TelegramError as e:
                    logger.error(f"Invalid chat ID {chat_id}: {e}")
            
            if valid_chats:
                logger.info(f"Successfully validated {len(valid_chats)}/{len(self.chat_ids)} chat IDs")
                return True
            else:
                logger.error("No valid chat IDs found")
                return False
                
        except TelegramError as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection test: {e}", exc_info=True)
            return False
    
    def test_connection_sync(self) -> bool:
        """Synchronous wrapper for testing connection."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.test_connection())

