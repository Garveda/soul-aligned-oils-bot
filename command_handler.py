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
        
        # Repeat command - allow scheduling message repeats
        if cmd_lower.startswith('repeat'):
            return self._handle_repeat(user_id, text, language)
        
        # Info command - only allow for today's primary/alternative oils
        if cmd_lower.startswith('info'):
            return self._handle_info(user_id, text, language)
        
        # Log disallowed/unknown commands for analytics, but do not reply verbosely
        self.db.log_command(user_id, 'unknown_or_blocked', text, False)
        try:
            self.db.log_interaction_attempt(
                user_id=user_id,
                attempted_command=text,
                was_allowed=False,
                oil_requested=None,
                daily_primary_oil=None,
                daily_alternative_oil=None,
            )
        except Exception:
            # Logging should never break command processing
            logger.debug("Failed to log interaction attempt", exc_info=True)
        
        # Optionally return a very gentle hint; to stay minimal we return None (silent ignore)
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
            elif language == 'hu':
                return "❌ Kérjük, add meg az időt HH:MM formátumban, pl. 'Repeat 14:30'"
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
                elif language == 'hu':
                    return "❌ Ez az idő már elmúlt. Kérjük, válassz egy jövőbeli időpontot."
                else:
                    return "❌ This time has already passed. Please choose a future time."
            
            # Schedule repeat
            self.db.schedule_repeat(user_id, date.today(), repeat_time)
            self.db.log_command(user_id, 'repeat', text, True)
            
            if language == 'de':
                return f"✅ Ich schicke dir die heutige Nachricht nochmal um {hour:02d}:{minute:02d} Uhr 🔄"
            elif language == 'hu':
                return f"✅ Újra elküldöm a mai üzenetet {hour:02d}:{minute:02d}-kor 🔄"
            else:
                return f"✅ I'll send you today's message again at {hour:02d}:{minute:02d} 🔄"
        except ValueError as e:
            self.db.log_command(user_id, 'repeat', text, False)
            if language == 'de':
                return "❌ Ungültige Zeit. Bitte verwende das Format HH:MM (z.B. 14:30)"
            elif language == 'hu':
                return "❌ Érvénytelen idő. Kérjük, használd a HH:MM formátumot (pl. 14:30)"
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
        
        # Generate alternative message (excluding already sent oils and recently used oils)
        primary_oil = daily_msg.get('primary_oil')
        alternative_oil = daily_msg.get('alternative_oil')
        
        # Generate new alternative message, excluding today's oils and recently used oils
        result_data = self.generator.generate_daily_message(
            language, 
            exclude_oils=[primary_oil, alternative_oil],
            user_id=user_id
        )
        
        if result_data and result_data.get('message'):
            message = result_data['message']
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
        """Handle info command for oil information (only today's oils allowed)."""
        from datetime import date as _date_cls  # local import to avoid circular issues in type hints
        
        # Extract oil name from command
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            self.db.log_command(user_id, 'info', text, False)
            # No explicit error message to keep interaction minimal
            return None
        
        oil_query = parts[1].strip()
        
        # Get today's primary/alternative oils from cached daily message
        today = _date_cls.today()
        daily_msg = self.db.get_daily_message(user_id, today)
        
        primary_oil = daily_msg.get('primary_oil') if daily_msg else None
        alternative_oil = daily_msg.get('alternative_oil') if daily_msg else None
        
        primary_lower = primary_oil.lower() if primary_oil else None
        alternative_lower = alternative_oil.lower() if alternative_oil else None
        requested_lower = oil_query.lower()
        
        # Check if requested oil matches today's primary or alternative
        is_primary = primary_lower and requested_lower == primary_lower
        is_alternative = alternative_lower and requested_lower == alternative_lower
        
        # Log interaction attempt
        try:
            self.db.log_interaction_attempt(
                user_id=user_id,
                attempted_command=text,
                was_allowed=bool(is_primary or is_alternative),
                oil_requested=oil_query,
                daily_primary_oil=primary_oil,
                daily_alternative_oil=alternative_oil,
            )
        except Exception:
            logger.debug("Failed to log interaction attempt for info", exc_info=True)
        
        if not (is_primary or is_alternative):
            # Politely restrict to today's oils only
            self.db.log_command(user_id, 'info_rejected', oil_query, False)
            if primary_oil or alternative_oil:
                if language == 'de':
                    return f"Ich kann dir heute nur Details zu {primary_oil or ''} oder {alternative_oil or ''} geben 🌿"
                elif language == 'hu':
                    return f"Ma csak {primary_oil or ''} vagy {alternative_oil or ''} részleteit tudom megadni 🌿"
                else:
                    return f"Today I can only provide details about {primary_oil or ''} or {alternative_oil or ''} 🌿"
            else:
                # No cached oils for today yet
                if language == 'de':
                    return "Ich kann dir Details geben, sobald du die heutige Morgennachricht erhalten hast 🌿"
                elif language == 'hu':
                    return "Amint megkapod a mai reggeli üzenetet, tudok részleteket adni 🌿"
                else:
                    return "I can share details once you have received today's morning message 🌿"
        
        # At this point we know the user requested today's primary or alternative oil
        oil_name_to_fetch = primary_oil if is_primary else alternative_oil
        oil_data = self.db.get_oil(oil_name_to_fetch)
        
        if not oil_data:
            self.db.log_command(user_id, 'info_missing_oil_data', oil_name_to_fetch, False)
            # Fall back to a simple message if the oil is not in the database yet
            if language == 'de':
                return f"Ich habe leider noch keine detaillierten Daten zu {oil_name_to_fetch} gespeichert 🌿"
            elif language == 'hu':
                return f"Sajnos még nincsenek részletes adataim erről az olajról: {oil_name_to_fetch} 🌿"
            else:
                return f"Unfortunately I don't have detailed data stored yet for {oil_name_to_fetch} 🌿"
        
        # Build detailed info message (multi-language template)
        self.db.log_command(user_id, 'info', oil_name_to_fetch, True)
        return self._format_detailed_oil_info(oil_data, language)
    
    def _format_oil_info(self, oil_data: Dict, language: str) -> str:
        """Format oil information for display."""
        # Legacy compact formatter (kept for backward compatibility if needed)
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

    def _format_detailed_oil_info(self, oil_data: Dict, language: str) -> str:
        """Format detailed oil information using structured, multi-language templates."""
        # Common pieces
        oil_name = oil_data.get('oil_name', '')
        botanical_name = ""  # Placeholder until extended schema is available
        energetic = oil_data.get('energetic_effects', '')
        interesting = oil_data.get('interesting_facts', '')
        contraindications = oil_data.get('contraindications', '')
        components = oil_data.get('main_components') or []
        best_uses = oil_data.get('best_uses') or []

        # Format components list (up to 3 for brevity)
        components_lines = []
        for comp in components[:3]:
            if isinstance(comp, dict):
                name = comp.get('name', '')
                percentage = comp.get('percentage', '')
                effect = comp.get('effect', '') or comp.get('effect_en', '')
                if percentage:
                    components_lines.append(f"- {name} ({percentage}): {effect}")
                else:
                    components_lines.append(f"- {name}: {effect}")
            else:
                components_lines.append(f"- {comp}")
        components_block = "\n".join(components_lines) if components_lines else ""

        # Format best uses as bullet list - EXCLUDE internal use for safety
        safe_uses = [u for u in best_uses if u and 'internal' not in u.lower() and 'intern' not in u.lower() and 'belső' not in u.lower()]
        uses_block = "\n".join(f"- {u}" for u in safe_uses) if safe_uses else ""

        if language == 'hu':
            # Hungarian template (headings HU, content from current DB fields)
            msg = f"🌿 {oil_name}\n{botanical_name}\n\n"
            if energetic:
                msg += "✨ ENERGETIKAI HATÁS\n"
                msg += f"{energetic}\n\n"
            msg += "💚 ÉRZELMI ELŐNYÖK\n"
            if energetic:
                msg += f"- {energetic}\n\n"
            else:
                msg += "- (adat feltöltés alatt)\n\n"
            if components_block:
                msg += "🔬 FŐ ÖSSZETEVŐK\n"
                msg += f"{components_block}\n\n"
            if interesting:
                msg += "📖 ÉRDEKES TÉNYEK\n"
                msg += f"{interesting}\n\n"
            if uses_block:
                msg += "💧 ALKALMAZÁS\n"
                msg += f"{uses_block}\n\n"
            if contraindications:
                msg += "⚠️ BIZTONSÁGI MEGJEGYZÉSEK\n"
                msg += f"{contraindications}\n\n"
            msg += "⚠️ FONTOS: Minden olaj kizárólag külső használatra. Soha ne fogyassz belsőleg professzionális útmutatás nélkül.\n\n"
            msg += "---\nSoul Aligned Oils 💜"
            return msg

        if language == 'en':
            # English template
            msg = f"🌿 {oil_name}\n{botanical_name}\n\n"
            if energetic:
                msg += "✨ ENERGETIC EFFECTS\n"
                msg += f"{energetic}\n\n"
            msg += "💚 EMOTIONAL BENEFITS\n"
            if energetic:
                msg += f"- {energetic}\n\n"
            else:
                msg += "- (data will be expanded soon)\n\n"
            if components_block:
                msg += "🔬 MAIN COMPONENTS\n"
                msg += f"{components_block}\n\n"
            if interesting:
                msg += "📖 INTERESTING FACTS\n"
                msg += f"{interesting}\n\n"
            if uses_block:
                msg += "💧 APPLICATION\n"
                msg += f"{uses_block}\n\n"
            if contraindications:
                msg += "⚠️ SAFETY NOTES\n"
                msg += f"{contraindications}\n\n"
            msg += "⚠️ IMPORTANT: All oils are for external use only. Never ingest essential oils without professional guidance.\n\n"
            msg += "---\nSoul Aligned Oils 💜"
            return msg

        # Default to German template
        msg = f"🌿 {oil_name}\n{botanical_name}\n\n"
        if energetic:
            msg += "✨ ENERGETISCHE WIRKUNG\n"
            msg += f"{energetic}\n\n"
        msg += "💚 EMOTIONALE VORTEILE\n"
        if energetic:
            msg += f"- {energetic}\n\n"
        else:
            msg += "- (Daten werden noch ergänzt)\n\n"
        if components_block:
            msg += "🔬 HAUPTINHALTSSTOFFE\n"
            msg += f"{components_block}\n\n"
        if interesting:
            msg += "📖 WISSENSWERTES\n"
            msg += f"{interesting}\n\n"
        if uses_block:
            msg += "💧 ANWENDUNG\n"
            msg += f"{uses_block}\n\n"
            if contraindications:
                msg += "⚠️ SICHERHEITSHINWEISE\n"
                msg += f"{contraindications}\n\n"
            msg += "⚠️ WICHTIG: Alle Öle sind ausschließlich für externe Anwendung. Niemals ohne professionelle Anleitung einnehmen.\n\n"
            msg += "---\nSoul Aligned Oils 💜"
            return msg
