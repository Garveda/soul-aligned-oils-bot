"""
Command Handler Module
Processes user commands and generates appropriate responses.
"""

import re
import logging
from datetime import datetime, time, date
from typing import Optional, Dict

from database import Database
from affirmation_generator import AffirmationGenerator
from config import Config

logger = logging.getLogger(__name__)


class CommandHandler:
    """Handles user commands and generates responses."""
    
    def __init__(self, db: Database, generator: AffirmationGenerator):
        """Initialize command handler."""
        self.db = db
        self.generator = generator
        logger.info("Command handler initialized")
    
    def process_command(self, user_id: str, text: str, language: str = 'de') -> Optional[str]:
        """Process a user command and return response message."""
        text = text.strip()
        
        # Check for emoji reactions
        if text in ['👍', '👎', '✅', '❌']:
            return self._handle_reaction(user_id, text)
        
        # Normalize command
        cmd_lower = text.lower()
        
        # Help command
        if cmd_lower in ['hilfe', 'help', '?', '/help', '/hilfe']:
            return self._handle_help(language)
        
        # Repeat command
        if cmd_lower.startswith('repeat') or re.match(r'repeat\s+\d+', cmd_lower):
            return self._handle_repeat(user_id, text, language)
        
        # Alternative command
        if cmd_lower in ['alternative', 'alternativ', 'alt']:
            return self._handle_alternative(user_id, language)
        
        # Info command
        if cmd_lower.startswith('info'):
            return self._handle_info(user_id, text, language)
        
        # Unknown command
        self.db.log_command(user_id, 'unknown', text, False)
        return None
    
    def _handle_reaction(self, user_id: str, reaction: str) -> str:
        """Handle emoji reaction."""
        today = date.today()
        self.db.add_reaction(user_id, today, reaction)
        self.db.log_command(user_id, 'reaction', reaction, True)
        
        if reaction in ['👍', '✅']:
            return "🙏 Danke für dein Feedback! Ich freue mich, dass dir die Nachricht gefällt. 💜"
        else:
            return "🙏 Danke für dein Feedback! Ich werde die Nachricht für morgen anpassen. 💜"
    
    def _handle_help(self, language: str) -> str:
        """Generate help message."""
        if language == 'de':
            return """📱 *Verfügbare Befehle:*

👍/👎 Reagiere auf Nachrichten mit Emojis

*Repeat [Zeit]* - Heutige Nachricht wiederholen
Beispiel: `Repeat 14:30` oder `Repeat 2:30pm`

*Alternative* - Andere Ölempfehlung für heute anfordern

*Info [Ölname]* - Detaillierte Informationen zu einem Öl
Beispiel: `Info Lavendel` oder `Info Lavender`

*Hilfe* - Diese Übersicht anzeigen

Mit Liebe,
Soul Aligned Oils 💜"""
        else:
            return """📱 *Available Commands:*

👍/👎 React to messages with emojis

*Repeat [TIME]* - Repeat today's message
Example: `Repeat 14:30` or `Repeat 2:30pm`

*Alternative* - Request alternative oil recommendation for today

*Info [OIL NAME]* - Get detailed information about an oil
Example: `Info Lavender`

*Help* - Show this overview

With love,
Soul Aligned Oils 💜"""
    
    def _handle_repeat(self, user_id: str, text: str, language: str) -> Optional[str]:
        """Handle repeat command."""
        # Extract time from command
        time_pattern = r'(\d{1,2}):(\d{2})'
        match = re.search(time_pattern, text)
        
        if not match:
            self.db.log_command(user_id, 'repeat', text, False)
            if language == 'de':
                return "❌ Bitte gib die Zeit im Format HH:MM an, z.B. 'Repeat 14:30'"
            else:
                return "❌ Please provide time in HH:MM format, e.g. 'Repeat 14:30'"
        
        hour = int(match.group(1))
        minute = int(match.group(2))
        
        # Check for PM indicator
        if 'pm' in text.lower() and hour < 12:
            hour += 12
        elif 'am' in text.lower() and hour == 12:
            hour = 0
        
        try:
            repeat_time = time(hour, minute)
            now = datetime.now()
            repeat_datetime = datetime.combine(date.today(), repeat_time)
            
            # Check if time is in the past
            if repeat_datetime <= now:
                self.db.log_command(user_id, 'repeat', text, False)
                if language == 'de':
                    return "❌ Diese Zeit ist bereits vorbei. Bitte wähle eine Zeit in der Zukunft."
                else:
                    return "❌ This time has already passed. Please choose a future time."
            
            # Schedule repeat
            self.db.schedule_repeat(user_id, date.today(), repeat_time)
            self.db.log_command(user_id, 'repeat', text, True)
            
            if language == 'de':
                return f"✅ Ich schicke dir die heutige Nachricht nochmal um {hour:02d}:{minute:02d} Uhr 🔄"
            else:
                return f"✅ I'll send you today's message again at {hour:02d}:{minute:02d} 🔄"
        except ValueError as e:
            self.db.log_command(user_id, 'repeat', text, False)
            if language == 'de':
                return "❌ Ungültige Zeit. Bitte verwende das Format HH:MM (z.B. 14:30)"
            else:
                return "❌ Invalid time. Please use HH:MM format (e.g. 14:30)"
    
    def _handle_alternative(self, user_id: str, language: str) -> Optional[str]:
        """Handle alternative oil recommendation request."""
        # Get today's message to see what oils were already recommended
        today = date.today()
        daily_msg = self.db.get_daily_message(user_id, today)
        
        if not daily_msg:
            if language == 'de':
                return "❌ Ich habe heute noch keine Nachricht für dich gesendet. Bitte warte auf die Morgennachricht."
            else:
                return "❌ I haven't sent you a message today yet. Please wait for the morning message."
        
        # Generate alternative message (excluding already sent oils)
        primary_oil = daily_msg.get('primary_oil')
        alternative_oil = daily_msg.get('alternative_oil')
        
        # Generate new alternative message
        # This would require updating the generator to exclude specific oils
        # For now, we'll generate a new message
        message = self.generator.generate_daily_message(language, exclude_oils=[primary_oil, alternative_oil])
        
        if message:
            self.db.log_command(user_id, 'alternative', None, True)
            if language == 'de':
                return f"🌿 *Alternative Empfehlung für heute:*\n\n{message}"
            else:
                return f"🌿 *Alternative Recommendation for Today:*\n\n{message}"
        else:
            self.db.log_command(user_id, 'alternative', None, False)
            if language == 'de':
                return "❌ Fehler beim Generieren der Alternativempfehlung. Bitte versuche es später erneut."
            else:
                return "❌ Error generating alternative recommendation. Please try again later."
    
    def _handle_info(self, user_id: str, text: str, language: str) -> Optional[str]:
        """Handle info command for oil information."""
        # Extract oil name from command
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            self.db.log_command(user_id, 'info', text, False)
            if language == 'de':
                return "❌ Bitte gib einen Ölnamen an, z.B. 'Info Lavendel'"
            else:
                return "❌ Please provide an oil name, e.g. 'Info Lavender'"
        
        oil_query = parts[1].strip()
        
        # Try to find the oil
        oil_data = self.db.get_oil(oil_query)
        
        if not oil_data:
            # Try fuzzy search
            all_oils = self.db.search_oils(oil_query, limit=5)
            if all_oils:
                self.db.log_command(user_id, 'info', text, False)
                if language == 'de':
                    suggestions = '\n'.join([f"- {oil}" for oil in all_oils])
                    return f"❌ Öl '{oil_query}' nicht gefunden. Meintest du vielleicht:\n{suggestions}"
                else:
                    suggestions = '\n'.join([f"- {oil}" for oil in all_oils])
                    return f"❌ Oil '{oil_query}' not found. Did you mean:\n{suggestions}"
            else:
                self.db.log_command(user_id, 'info', text, False)
                if language == 'de':
                    return f"❌ Das Öl '{oil_query}' kenne ich noch nicht. Schreib 'Hilfe' für verfügbare Befehle."
                else:
                    return f"❌ I don't know the oil '{oil_query}' yet. Write 'Help' for available commands."
        
        # Build info message
        self.db.log_command(user_id, 'info', oil_query, True)
        return self._format_oil_info(oil_data, language)
    
    def _format_oil_info(self, oil_data: Dict, language: str) -> str:
        """Format oil information for display."""
        if language == 'de':
            msg = f"🌿 *{oil_data['oil_name']}*\n\n"
            
            if oil_data.get('energetic_effects'):
                msg += f"*Energetische Wirkung:*\n{oil_data['energetic_effects']}\n\n"
            
            if oil_data.get('main_components'):
                msg += "*Hauptinhaltsstoffe:*\n"
                for component in oil_data['main_components'][:5]:  # Limit to 5
                    if isinstance(component, dict):
                        comp_name = component.get('name', '')
                        comp_effect = component.get('effect', '')
                        msg += f"- {comp_name}: {comp_effect}\n"
                    else:
                        msg += f"- {component}\n"
                msg += "\n"
            
            if oil_data.get('interesting_facts'):
                msg += f"*Wissenswertes:*\n{oil_data['interesting_facts']}\n\n"
            
            if oil_data.get('contraindications'):
                msg += f"*⚠️ Hinweise:*\n{oil_data['contraindications']}\n\n"
            
            if oil_data.get('best_uses'):
                msg += "*Beste Anwendung:*\n"
                for use in oil_data['best_uses']:
                    msg += f"- {use}\n"
            
            msg += "\n💜 Soul Aligned Oils"
            return msg
        else:
            msg = f"🌿 *{oil_data['oil_name']}*\n\n"
            
            if oil_data.get('energetic_effects'):
                msg += f"*Energetic Effects:*\n{oil_data['energetic_effects']}\n\n"
            
            if oil_data.get('main_components'):
                msg += "*Main Components:*\n"
                for component in oil_data['main_components'][:5]:
                    if isinstance(component, dict):
                        comp_name = component.get('name', '')
                        comp_effect = component.get('effect', '')
                        msg += f"- {comp_name}: {comp_effect}\n"
                    else:
                        msg += f"- {component}\n"
                msg += "\n"
            
            if oil_data.get('interesting_facts'):
                msg += f"*Interesting Facts:*\n{oil_data['interesting_facts']}\n\n"
            
            if oil_data.get('contraindications'):
                msg += f"*⚠️ Safety Notes:*\n{oil_data['contraindications']}\n\n"
            
            if oil_data.get('best_uses'):
                msg += "*Best Uses:*\n"
                for use in oil_data['best_uses']:
                    msg += f"- {use}\n"
            
            msg += "\n💜 Soul Aligned Oils"
            return msg
