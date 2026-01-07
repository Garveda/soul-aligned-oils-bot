"""
Configuration module for Soul Aligned Oils bot.
Loads environment variables and provides configuration settings.
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the application."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_IDS: List[str] = os.getenv('TELEGRAM_CHAT_IDS', '').split(',')
    CHAT_LANGUAGES: List[str] = os.getenv('CHAT_LANGUAGES', '').split(',')  # Language per chat ID (en, de, etc.)
    
    # Scheduling Configuration
    SEND_TIME: str = os.getenv('SEND_TIME', '08:00')
    TIMEZONE: str = os.getenv('TIMEZONE', 'Europe/Berlin')
    
    # Application Configuration
    TESTING_MODE: bool = os.getenv('TESTING_MODE', 'False').lower() == 'true'
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Data paths
    OILS_DATABASE_PATH: str = os.path.join(
        os.path.dirname(__file__), 
        'data', 
        'doterra_oils.json'
    )
    LOG_FILE_PATH: str = os.path.join(
        os.path.dirname(__file__), 
        'logs', 
        'bot.log'
    )
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate that all required configuration values are set.
        
        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set")
        
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is not set")
        
        if not cls.TELEGRAM_CHAT_IDS or cls.TELEGRAM_CHAT_IDS == ['']:
            errors.append("TELEGRAM_CHAT_IDS is not set")
        
        if errors:
            for error in errors:
                print(f"Configuration Error: {error}")
            return False
        
        return True
    
    @classmethod
    def get_send_hour_minute(cls) -> tuple:
        """
        Parse SEND_TIME into hour and minute.
        
        Returns:
            tuple: (hour, minute) as integers
        """
        try:
            hour, minute = cls.SEND_TIME.split(':')
            return int(hour), int(minute)
        except (ValueError, AttributeError):
            print(f"Invalid SEND_TIME format: {cls.SEND_TIME}. Using default 08:00")
            return 8, 0
    
    @classmethod
    def get_language_for_chat(cls, chat_id: str) -> str:
        """
        Get the language preference for a specific chat ID.
        
        Args:
            chat_id: The chat ID to look up
            
        Returns:
            str: Language code (default: 'en')
        """
        try:
            chat_ids = [cid.strip() for cid in cls.TELEGRAM_CHAT_IDS if cid.strip()]
            languages = [lang.strip() for lang in cls.CHAT_LANGUAGES if lang.strip()]
            
            # If no languages specified, default to English
            if not languages or languages == ['']:
                return 'en'
            
            # Find index of chat_id
            if chat_id in chat_ids:
                idx = chat_ids.index(chat_id)
                # Return corresponding language if it exists, otherwise default to first language
                if idx < len(languages):
                    return languages[idx]
                elif languages:
                    return languages[0]
            
            return 'en'
        except Exception:
            return 'en'

