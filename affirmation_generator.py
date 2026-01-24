"""
Affirmation Generator Module
Integrates with OpenAI API to generate personalized daily affirmations
with doTerra essential oil recommendations in multiple languages.
"""

import json
import logging
import random
from datetime import datetime
from typing import Dict, List, Optional
from openai import OpenAI

from config import Config

# Set up logging
logger = logging.getLogger(__name__)


class AffirmationGenerator:
    """Generates AI-powered affirmations with essential oil recommendations."""
    
    # Weekday Planetary Energy Characteristics
    DAY_ENERGY = {
        'Monday': {
            'planet': 'Moon',
            'theme': 'Emotions, deep feeling, intuition, premonition',
            'focus': 'Connect with yourself, emotions, inner intuition',
            'activities': 'Journaling, mindfulness exercises, feeling'
        },
        'Tuesday': {
            'planet': 'Mars',
            'theme': 'Action, drive, courage, bringing fire back',
            'focus': 'Acting, taking initiative, moving forward with clarity',
            'activities': 'Making decisions, speaking clearly, freeing energy, taking action on projects'
        },
        'Wednesday': {
            'planet': 'Mercury',
            'theme': 'Communication, friendship, siblings',
            'focus': 'Lighter energy, sorting thoughts, exchanging ideas',
            'activities': 'Workshops, Q&As, content creation, reflecting on decisions, clarifying conversations'
        },
        'Thursday': {
            'planet': 'Jupiter',
            'theme': 'Growth, expansion, vision',
            'focus': 'Looking beyond the horizon, expansion through trust, manifestation',
            'activities': 'Vision boarding, investing in yourself, financial conversations'
        },
        'Friday': {
            'planet': 'Venus',
            'theme': 'Letting go well, self-love, love, meaning, relaxation',
            'focus': 'Enjoyment, social connections, opening your heart',
            'activities': 'Dates, enjoying time with others and yourself, speaking beautifully about yourself'
        },
        'Saturday': {
            'planet': 'Saturn',
            'theme': 'Structure, responsibility, order, setting boundaries',
            'focus': 'Maturity of the week, organizing, cleaning out',
            'activities': 'Sorting, decluttering, clarifying'
        },
        'Sunday': {
            'planet': 'Sun',
            'theme': 'Active day, yang energy, feeling into what you liked',
            'focus': 'Returning to yourself, noticing what worked',
            'activities': 'Doing what you enjoy'
        }
    }
    
    # Month themes and focus areas
    MONTH_THEMES = {
        'January': {
            'theme': 'New Beginnings & Fresh Intentions',
            'focus': 'clarity, goal setting, renewal, purification, fresh start energy',
            'energy': 'Clean slate, new year momentum, determination, clarity of vision'
        },
        'February': {
            'theme': 'Self-Love & Heart Connection',
            'focus': 'self-compassion, heart healing, love, emotional warmth, inner acceptance',
            'energy': 'Love yourself first, heart-centered living, emotional nurturing, tenderness'
        },
        'March': {
            'theme': 'Awakening & Rebirth',
            'focus': 'spring awakening, growth, vitality, rebirth, emerging energy',
            'energy': 'Nature awakening, fresh growth, renewed vitality, blossoming potential'
        },
        'April': {
            'theme': 'Growth & Expansion',
            'focus': 'flowering, manifestation, joy, growth, creative expression',
            'energy': 'Full bloom energy, expansion, creative flow, joyful manifestation'
        },
        'May': {
            'theme': 'Abundance & Gratitude',
            'focus': 'abundance mindset, gratitude, appreciation, fullness, prosperity',
            'energy': 'Abundant blessings, grateful heart, prosperity consciousness, fullness of life'
        },
        'June': {
            'theme': 'Light & Radiance',
            'focus': 'inner light, radiance, confidence, brightness, solar energy',
            'energy': 'Maximum light, radiant confidence, summer vitality, brightness of being'
        },
        'July': {
            'theme': 'Freedom & Joy',
            'focus': 'liberation, joy, celebration, independence, authentic expression',
            'energy': 'Freedom to be yourself, joyful celebration, authentic living, liberation'
        },
        'August': {
            'theme': 'Power & Strength',
            'focus': 'personal power, inner strength, courage, leadership, boldness',
            'energy': 'Peak power, inner strength, courageous action, stepping into leadership'
        },
        'September': {
            'theme': 'Harvest & Reflection',
            'focus': 'reaping rewards, reflection, wisdom, preparation, harvest time',
            'energy': 'Harvest your efforts, reflect on growth, gather wisdom, prepare for change'
        },
        'October': {
            'theme': 'Transformation & Release',
            'focus': 'letting go, transformation, deep change, shedding old patterns',
            'energy': 'Release what no longer serves, transformation, deep inner change, renewal through release'
        },
        'November': {
            'theme': 'Gratitude & Inner Warmth',
            'focus': 'thankfulness, inner warmth, appreciation, cozy comfort, heart gratitude',
            'energy': 'Deep gratitude, counting blessings, inner warmth, thankful heart'
        },
        'December': {
            'theme': 'Reflection & Sacred Rest',
            'focus': 'rest, reflection, sacred pause, completion, spiritual connection',
            'energy': 'Year-end reflection, sacred rest, completion of cycles, quiet contemplation'
        }
    }
    
    # Seasonal oil preferences
    SEASONAL_OILS = {
        'winter': ['Cinnamon', 'Ginger', 'Eucalyptus', 'On Guard', 'Breathe', 'Frankincense', 'Cedarwood'],
        'spring': ['Lemon', 'Grapefruit', 'Peppermint', 'Citrus Bliss', 'Bergamot', 'Wild Orange'],
        'summer': ['Lime', 'Wild Orange', 'Peppermint', 'Elevation', 'Lemon', 'Grapefruit'],
        'autumn': ['Cedarwood', 'Frankincense', 'Balance', 'Tea Tree', 'Cinnamon', 'Sandalwood']
    }
    
    # Lunar/Portal day oils
    LUNAR_OILS = {
        'new_moon': ['Frankincense', 'Sandalwood', 'Cedarwood', 'Balance'],
        'full_moon': ['Lavender', 'Clary Sage', 'Ylang Ylang', 'Bergamot', 'Peace & Calming'],
        'portal': ['Vetiver', 'Balance', 'Peace & Calming', 'Frankincense', 'Cedarwood']
    }
    
    # Most commonly used oils - alternative oil should always be from this list
    COMMONLY_USED_OILS = [
        'Lavender', 'Peppermint', 'Lemon', 'Frankincense', 'Wild Orange',
        'Eucalyptus', 'Tea Tree (Melaleuca)', 'Cedarwood', 'Bergamot', 'Rosemary',
        'Ginger', 'Cinnamon Bark', 'Balance (Grounding Blend)', 'Breathe (Respiratory Blend)',
        'On Guard (Protective Blend)', 'Deep Blue (Soothing Blend)', 'DigestZen (Digestive Blend)',
        'Serenity (Restful Blend)', 'Peace (Reassuring Blend)', 'Elevation (Joyful Blend)',
        'Grapefruit', 'Lime', 'Clary Sage', 'Ylang Ylang', 'Vetiver', 'Sandalwood'
    ]
    
    def __init__(self, db=None, lunar_calendar=None):
        """Initialize the affirmation generator."""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.oils = self._load_oils()
        self.db = db
        self.lunar_calendar = lunar_calendar
        
    def _load_oils(self) -> List[Dict]:
        """Load doTerra oils from JSON database."""
        try:
            with open(Config.OILS_DATABASE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data['oils'])} oils from database")
                return data['oils']
        except FileNotFoundError:
            logger.error(f"Oils database not found at {Config.OILS_DATABASE_PATH}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing oils database: {e}")
            raise
    
    def _get_oil_list_string(self) -> str:
        """Create a formatted string of available oils for the prompt."""
        oil_strings = []
        for oil in self.oils:
            properties = ', '.join(oil['properties'][:4])
            oil_strings.append(f"- {oil['name']} ({properties})")
        return '\n'.join(oil_strings)
    
    def _get_current_season(self, check_date: datetime = None) -> str:
        """Determine current season."""
        if check_date is None:
            check_date = datetime.now()
        
        month = check_date.month
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'autumn'
    
    def _get_current_day_info(self, check_date: datetime = None) -> tuple:
        """Get current day and month information."""
        if check_date is None:
            check_date = datetime.now()
        
        day_name = check_date.strftime('%A')
        month_name = check_date.strftime('%B')
        date_string = check_date.strftime('%B %d, %Y')
        day_energy = self.DAY_ENERGY.get(day_name, {
            'planet': 'Balance',
            'theme': 'Balance and presence',
            'focus': 'Centering yourself',
            'activities': 'Mindfulness'
        })
        month_info = self.MONTH_THEMES.get(month_name, {
            'theme': 'Balance & Presence',
            'focus': 'mindfulness, presence, balance',
            'energy': 'Present moment awareness'
        })
        return day_name, month_name, date_string, day_energy, month_info
    
    def _create_prompt(self, language: str = 'en') -> str:
        """Create the GPT prompt for generating the daily message."""
        day_name, month_name, date_string, day_energy, month_info = self._get_current_day_info()
        oil_list = self._get_oil_list_string()
        
        if language == 'de':
            return self._create_german_prompt(day_name, month_name, date_string, day_energy, month_info, oil_list)
        else:
            return self._create_english_prompt(day_name, month_name, date_string, day_energy, month_info, oil_list)
    
    def _create_english_prompt(self, day_name: str, month_name: str, date_string: str, day_energy: dict, month_info: dict, oil_list: str) -> str:
        """Create English version of the prompt - SHORT and PRACTICAL."""
        return f"""You are a holistic wellness guide. Create a SHORT, PRACTICAL daily message.

TODAY: {day_name} ({day_energy['planet']} Energy) - {date_string}
Weekday Theme: {day_energy['theme']}
Weekday Focus: {day_energy['focus']}

MONTH: {month_name} - {month_info['theme']}

CRITICAL REQUIREMENTS:
1. KEEP IT SHORT - Maximum 3-4 brief paragraphs
2. PRACTICAL - Must fit into daily life
3. TWO OILS - Primary + Alternative recommendation
4. SIMPLE RITUAL - 1-2 sentences maximum

STRUCTURE (follow EXACTLY):

🌙 Guten Morgen

[2-3 sentence affirmation connected to {day_name}'s {day_energy['planet']} energy theme: {day_energy['theme']}]

🌿 Deine Öl-Begleiter für heute:
- [Primary Oil Name]: [ONE sentence benefit for today's energy]
- Alternativ: [Alternative Oil Name]: [ONE sentence benefit]

✨ Dein Ritual:
[1-2 sentences with simple, actionable instruction]

Mit Liebe,
Soul Aligned Oils 💜

AVAILABLE OILS:
{oil_list}

IMPORTANT:
- Maximum 3-4 short paragraphs total
- Affirmation: 2-3 sentences, aligned with {day_name}'s {day_energy['planet']} energy
- TWO oils that match {day_name}'s theme: {day_energy['theme']}
- Oil benefits: ONE sentence each
- Ritual: 1-2 sentences, simple and doable
- Use emojis ONLY as shown in structure
- Keep tone warm but CONCISE
"""
    
    def _create_german_prompt(self, day_name: str, month_name: str, date_string: str, day_energy: dict, month_info: dict, oil_list: str) -> str:
        """Create German version of the prompt - SHORT and PRACTICAL."""
        day_names_de = {
            'Monday': 'Montag', 'Tuesday': 'Dienstag', 'Wednesday': 'Mittwoch',
            'Thursday': 'Donnerstag', 'Friday': 'Freitag', 'Saturday': 'Samstag', 'Sunday': 'Sonntag'
        }
        month_names_de = {
            'January': 'Januar', 'February': 'Februar', 'March': 'März', 'April': 'April',
            'May': 'Mai', 'June': 'Juni', 'July': 'Juli', 'August': 'August',
            'September': 'September', 'October': 'Oktober', 'November': 'November', 'December': 'Dezember'
        }
        planet_names_de = {
            'Moon': 'Mond', 'Mars': 'Mars', 'Mercury': 'Merkur', 'Jupiter': 'Jupiter',
            'Venus': 'Venus', 'Saturn': 'Saturn', 'Sun': 'Sonne'
        }
        
        day_name_de = day_names_de.get(day_name, day_name)
        month_name_de = month_names_de.get(month_name, month_name)
        planet_de = planet_names_de.get(day_energy['planet'], day_energy['planet'])
        
        return f"""Erstelle eine WARMHERZIGE, EINFÜHLSAME tägliche Affirmation auf DEUTSCH.

KONTEXT FÜR HEUTE:
📅 {day_name_de} ({planet_de}-Energie) - {date_string}
💫 Wochentag-Energie: {day_energy['theme']}
🎯 Fokus: {day_energy['focus']}
📆 Monat: {month_name_de} - {month_info['theme']}

DEINE AUFGABE:
Erstelle eine Nachricht, die sich anfühlt wie ein warmes Gespräch mit einer Freundin. 
Die Affirmation soll:
- EMOTIONAL berühren und Mut machen
- PRAKTISCH sein und in den Alltag passen
- INTELLIGENT die heutige Energie nutzen
- NATÜRLICH fließen, nicht steif wirken
- KURZ bleiben (3-4 Absätze), aber substanziell sein

STRUKTUR:

🌙 Guten Morgen

[2-3 Sätze Affirmation - warm, persönlich, verbunden mit der {day_name_de}-{planet_de}-Energie. 
Sprich die Person direkt an, sei einfühlsam und ermutigend. Nutze die Energie von {day_energy['theme']} 
und verbinde sie mit {month_info['theme']}.]

🌿 Deine Öl-Begleiter für heute:
{f"- {selected_primary}: [Ein warmer, persönlicher Satz über den Nutzen - wie es sich anfühlt, nicht nur was es tut]" if selected_primary else "- [Haupt-Öl Name]: [Ein warmer Satz über den Nutzen]"}
{f"- Alternativ: {selected_alternative}: [Ein warmer, persönlicher Satz über den Nutzen]" if selected_alternative else "- Alternativ: [Alternatives Öl Name]: [Ein warmer Satz über den Nutzen]"}

{"⚠️ WICHTIG: Verwende GENAU diese beiden Öle: {selected_primary} (Haupt) und {selected_alternative} (Alternativ). Öl-Namen IMMER auf ENGLISCH!" if selected_primary and selected_alternative else ""}

✨ Dein Ritual:
[1-2 Sätze - eine einfache, einladende Anleitung, die sich gut anfühlt und leicht umsetzbar ist. 
Formuliere es wie eine freundliche Einladung, nicht wie eine Anweisung.]

Mit Liebe,
Soul Aligned Oils 💜

VERFÜGBARE ÖLE:
{oil_list}

WICHTIG FÜR DEN TON:
- Schreibe wie eine vertraute Freundin, die wirklich zuhört und versteht
- Sei warm, aber nicht übertrieben - authentisch und echt
- Nutze die Energie von {day_energy['theme']} intelligent, nicht mechanisch
- Verbinde {month_info['theme']} natürlich mit dem heutigen Tag
- Formuliere Öl-Nutzen persönlich: "Wie es sich anfühlt" statt nur "Was es tut"
- Ritual als freundliche Einladung, nicht als Pflicht
- Maximal 3-4 Absätze, aber jede Zeile soll Bedeutung haben
- Die GESAMTE Nachricht auf DEUTSCH
- ÖL-NAMEN: IMMER auf ENGLISCH (originale doTerra-Namen) - NIE übersetzen!
"""
    
    def _extract_oil_names(self, message: str) -> tuple:
        """Extract primary and alternative oil names from message."""
        primary_oil = None
        alternative_oil = None
        
        # Look for oil patterns in the message
        lines = message.split('\n')
        for i, line in enumerate(lines):
            # Primary oil: "- [Oil Name]:"
            if '- ' in line and ':' in line and 'Alternativ' not in line and '🌿' not in line:
                parts = line.split(':')
                if len(parts) > 0:
                    oil_part = parts[0].replace('-', '').strip()
                    # Try to match with known oils
                    for oil in self.oils:
                        if oil['name'].lower() in oil_part.lower():
                            primary_oil = oil['name']
                            break
            
            # Alternative oil: "- Alternativ: [Oil Name]:" or "- Alternativ: [Oil Name]"
            if 'Alternativ' in line or 'alternativ' in line:
                # Check next line or same line
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        oil_part = parts[1].strip().split()[0] if parts[1].strip() else None
                        if oil_part:
                            for oil in self.oils:
                                if oil['name'].lower() in oil_part.lower() or oil_part.lower() in oil['name'].lower():
                                    alternative_oil = oil['name']
                                    break
        
        return primary_oil, alternative_oil
    
    def _select_oils_programmatically(self, exclude_oils: List[str] = None, day_energy: Dict = None, 
                                      season: str = None, message_type: str = 'regular') -> tuple:
        """Programmatically select primary and alternative oils that haven't been used recently.
        
        Returns:
            tuple: (primary_oil_name, alternative_oil_name) or (None, None) if selection fails
        """
        if exclude_oils is None:
            exclude_oils = []
        
        # Get available oils (excluding recently used ones)
        available_oils = [oil for oil in self.oils if oil['name'] not in exclude_oils]
        
        if not available_oils:
            logger.warning(f"No available oils after excluding {len(exclude_oils)} oils. Using all oils.")
            available_oils = self.oils
        
        # Filter oils based on day energy and season if provided
        suitable_oils = []
        for oil in available_oils:
            # Check if oil properties match day energy theme
            oil_props = ' '.join(oil.get('properties', [])).lower()
            if day_energy:
                theme_words = day_energy.get('theme', '').lower().split()
                focus_words = day_energy.get('focus', '').lower().split()
                # Check if any property matches the theme
                matches_theme = any(word in oil_props for word in theme_words + focus_words if len(word) > 3)
                if matches_theme or len(suitable_oils) < 10:  # Keep at least 10 options
                    suitable_oils.append(oil)
            else:
                suitable_oils.append(oil)
        
        if not suitable_oils:
            suitable_oils = available_oils
        
        # Select primary oil (random from suitable oils)
        if suitable_oils:
            primary_oil = random.choice(suitable_oils)
        else:
            primary_oil = random.choice(available_oils) if available_oils else None
        
        # Select alternative oil from commonly used oils (excluding primary and recently used)
        # First try commonly used oils, but ensure variety by shuffling
        alternative_candidates = [
            oil for oil in available_oils 
            if oil['name'] in self.COMMONLY_USED_OILS and oil['name'] != primary_oil['name']
        ]
        
        # Shuffle to ensure better randomization
        if alternative_candidates:
            random.shuffle(alternative_candidates)
            alternative_oil = alternative_candidates[0]
            logger.info(f"Alternative oil selected from {len(alternative_candidates)} commonly used candidates")
        else:
            # Fallback: any available oil that's not the primary (shuffled for variety)
            fallback = [oil for oil in available_oils if oil['name'] != primary_oil['name']]
            if fallback:
                random.shuffle(fallback)
                alternative_oil = fallback[0]
                logger.warning(f"Alternative oil selected from fallback pool ({len(fallback)} oils available)")
            else:
                alternative_oil = None
        
        if primary_oil and alternative_oil:
            logger.info(f"Programmatically selected oils: Primary={primary_oil['name']}, Alternative={alternative_oil['name']}")
            return primary_oil['name'], alternative_oil['name']
        
        return None, None
    
    def generate_daily_message(self, language: str = 'en', exclude_oils: List[str] = None,
                              special_day_info: Dict = None, user_id: str = None) -> Dict:
        """Generate the complete daily affirmation message.
        
        Args:
            language: Language code ('de' or 'en')
            exclude_oils: List of oil names to exclude from recommendations
            special_day_info: Dict with 'message_type', 'moon_phase', 'is_portal_day' if applicable
            user_id: Optional user ID to automatically exclude recently used oils
            
        Returns:
            Dict with 'message', 'primary_oil', 'alternative_oil' keys, or None if generation fails
        """
        try:
            check_date = datetime.now()
            
            # If user_id is provided and we have database access, get recently used oils
            recently_used = []
            if user_id and self.db:
                recently_used = self.db.get_recently_used_oils(user_id, days=14)
                if exclude_oils is None:
                    exclude_oils = []
                # Combine with provided exclude_oils, removing duplicates
                exclude_oils = list(set(exclude_oils + recently_used))
                if recently_used:
                    logger.info(f"Excluding {len(recently_used)} recently used oils for user {user_id}: {recently_used[:5]}...")
            
            # Check for special days if lunar_calendar is available
            if special_day_info is None and self.lunar_calendar:
                special_day_info = self.lunar_calendar.get_special_day_info(check_date.date())
            
            # Determine message type priority
            message_type = 'regular'
            if special_day_info:
                message_type = special_day_info.get('message_type', 'regular')
            
            # Get day info for oil selection
            day_name, month_name, date_string, day_energy, month_info = self._get_current_day_info(check_date)
            season = self._get_current_season(check_date)
            
            # Programmatically select oils BEFORE generating message
            selected_primary, selected_alternative = self._select_oils_programmatically(
                exclude_oils=exclude_oils,
                day_energy=day_energy,
                season=season,
                message_type=message_type
            )
            
            # Create appropriate prompt with selected oils
            common_oils_str = ', '.join(self.COMMONLY_USED_OILS[:15])  # First 15 for brevity
            if message_type == 'portal':
                prompt = self._create_portal_prompt(language, special_day_info, common_oils_str, exclude_oils, selected_primary, selected_alternative)
            elif message_type == 'full_moon':
                prompt = self._create_full_moon_prompt(language, special_day_info, common_oils_str, exclude_oils, selected_primary, selected_alternative)
            elif message_type == 'new_moon':
                prompt = self._create_new_moon_prompt(language, special_day_info, common_oils_str, exclude_oils, selected_primary, selected_alternative)
            else:
                prompt = self._create_prompt(language, exclude_oils, selected_primary, selected_alternative)
            
            logger.info(f"Requesting affirmation from OpenAI API (language: {language}, type: {message_type})")
            
            # Customize system message based on language - smarter and more comfortable
            if language == 'de':
                system_content = """Du bist ein einfühlsamer, weiser Wellness-Guide mit tiefem Verständnis für menschliche Bedürfnisse. 
Du erstellst tägliche Affirmationen, die:
- WARM und EINLADEND sind, wie von einer vertrauten Freundin
- EMOTIONAL RESONANT sind und sich authentisch anfühlen
- PRAKTISCH und UMSETZBAR sind, ohne überwältigend zu wirken
- INTELLIGENT die Tagesenergie und Jahreszeit berücksichtigen
- KURZ bleiben (3-4 Absätze), aber trotzdem substanziell

🚨 KRITISCH - SICHERHEIT:
- ALLE Öl-Empfehlungen sind AUSSCHLIESSLICH für EXTERNE Anwendung
- NIEMALS vorschlagen, Öle zu trinken, zu schlucken, zu essen oder intern einzunehmen
- NIEMALS vorschlagen, Öle zu Wasser, Essen oder Getränken hinzuzufügen
- NIEMALS interne Einnahme, Kapseln oder orale Anwendung erwähnen
- NUR externe Anwendung: topisch (auf die Haut), aromatisch (Diffuser), oder in Trägeröl verdünnt

WICHTIG: Antworte IMMER auf DEUTSCH. Schreibe natürlich und fließend, nicht steif oder roboterhaft. 
KRITISCH: Öl-Namen müssen IMMER auf ENGLISCH sein (originale doTerra-Namen) - NIE übersetzen!"""
            elif language == 'hu':
                system_content = """Te egy empátiával teli, bölcs wellness útmutató vagy, aki mélyen érti az emberi szükségleteket.
Olyan napi megerősítéseket hozol létre, amelyek:
- MELEGEK és MEGNYERŐEK, mintha egy megbízható barátnő írná
- ÉRZELMILEG REZONÁLNAK és autentikusnak érződnek
- GYAKORLATIAK és MEGVALÓSÍTHATÓAK, anélkül hogy túlterhelőek lennének
- OKOSAN figyelembe veszik a nap energiáját és az évszakot
- RÖVIDEK maradnak (3-4 bekezdés), de mégis lényegretörőek

🚨 KRITIKUS - BIZTONSÁG:
- MINDEN olaj ajánlás KIZÁRÓLAG KÜLSŐ használatra szól
- SOHA ne javasolj olajok ivását, lenyelését, evését vagy belső fogyasztását
- SOHA ne javasolj olajok hozzáadását vízhez, ételhez vagy italhoz
- SOHA ne említs belső szedést, kapszulákat vagy orális alkalmazást
- CSAK külső használat: topikálisan (bőrre), aromatikusan (diffúzor), vagy hordozóolajban hígítva

FONTOS: Válaszolj MINDIG MAGYARUL. Írj természetesen és folyékonyan, ne mereven vagy robotikusan.
KRITIKUS: Az olajneveknek MINDIG ANGOLUL kell lenniük (eredeti doTerra nevek) - SOHA ne fordítsd le!"""
            else:
                system_content = """You are an empathetic, wise wellness guide with deep understanding of human needs.
You create daily affirmations that are:
- WARM and INVITING, like from a trusted friend
- EMOTIONALLY RESONANT and feel authentic
- PRACTICAL and ACTIONABLE without being overwhelming
- INTELLIGENTLY consider the day's energy and season
- SHORT (3-4 paragraphs) yet still substantial

🚨 CRITICAL - SAFETY:
- ALL oil recommendations are EXCLUSIVELY for EXTERNAL use only
- NEVER suggest drinking, swallowing, eating, or ingesting oils
- NEVER suggest adding oils to water, food, or beverages
- NEVER mention internal consumption, capsules, or oral application
- ONLY external use: topically (on skin), aromatically (diffuser), or diluted in carrier oil

Write naturally and fluidly, not stiff or robotic.
CRITICAL: Oil names must ALWAYS be in English (original doTerra names)."""
            
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=600
            )
            
            message = response.choices[0].message.content.strip()
            
            # CRITICAL SAFETY: Validate message for internal consumption suggestions
            unsafe_phrases = [
                'drink', 'ingest', 'consume', 'take internally', 'swallow', 
                'add to water', 'add to food', 'add to drink', 'oral', 
                'internally', 'capsule', 'kapsel', 'trinken', 'einnehmen',
                'belső', 'ivás', 'lenyel', 'kapszula', 'orális'
            ]
            
            message_lower = message.lower()
            detected_unsafe = [phrase for phrase in unsafe_phrases if phrase in message_lower]
            
            # Regenerate if unsafe phrases detected (max 3 attempts)
            max_attempts = 3
            attempt = 1
            
            while detected_unsafe and attempt < max_attempts:
                logger.warning(f"⚠️ SAFETY ALERT: Detected unsafe phrases in generated message: {detected_unsafe}. Regenerating (attempt {attempt}/{max_attempts})...")
                
                # Add stronger safety constraint to prompt
                safety_note = ""
                if language == 'de':
                    safety_note = "\n\n🚨 KRITISCH: Die vorherige Nachricht enthielt unsichere Formulierungen. Erstelle eine NEUE Nachricht, die AUSSCHLIESSLICH externe Anwendung erwähnt (topisch, aromatisch, in Trägeröl). NIEMALS interne Einnahme!"
                elif language == 'hu':
                    safety_note = "\n\n🚨 KRITIKUS: Az előző üzenet nem biztonságos kifejezéseket tartalmazott. Hozz létre egy ÚJ üzenetet, amely KIZÁRÓLAG külső használatot említ (topikális, aromatikus, hordozóolajban). SOHA ne belső szedés!"
                else:
                    safety_note = "\n\n🚨 CRITICAL: Previous message contained unsafe phrasing. Create a NEW message that mentions EXCLUSIVELY external use (topical, aromatic, in carrier oil). NEVER internal consumption!"
                
                response = self.client.chat.completions.create(
                    model=Config.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": prompt + safety_note}
                    ],
                    temperature=0.8,
                    max_tokens=600
                )
                
                message = response.choices[0].message.content.strip()
                message_lower = message.lower()
                detected_unsafe = [phrase for phrase in unsafe_phrases if phrase in message_lower]
                attempt += 1
            
            # If still unsafe after max attempts, use safe fallback
            if detected_unsafe:
                logger.error(f"⚠️ SAFETY ERROR: Unable to generate safe message after {max_attempts} attempts. Using safe fallback.")
                if language == 'de':
                    message = f"""🌙 Guten Morgen

Heute begleiten dich {selected_primary or 'deine Öle'} und {selected_alternative or 'deine Alternative'} auf deinem Weg.

🌿 Deine Öl-Begleiter für heute:
- {selected_primary or 'Haupt-Öl'}: Unterstützt dich heute in deiner Energie
- Alternativ: {selected_alternative or 'Alternatives Öl'}: Eine wunderbare Ergänzung

✨ Dein Ritual:
Nimm dir einen Moment für dich und nutze die Öle topisch oder aromatisch.

⚠️ Wichtig: Alle Öle sind ausschließlich für externe Anwendung. Niemals ohne professionelle Anleitung einnehmen.

Mit Liebe,
Soul Aligned Oils 💜"""
                elif language == 'hu':
                    message = f"""🌙 Jó reggelt

Ma {selected_primary or 'az olajaid'} és {selected_alternative or 'az alternatíváid'} kísérnek az úton.

🌿 Mai illóolaj társaid:
- {selected_primary or 'Fő olaj'}: Ma támogat az energiádban
- Alternatíva: {selected_alternative or 'Alternatív olaj'}: Csodálatos kiegészítés

✨ A te rituáléd:
Szánj magadra egy pillanatot és használd az olajokat topikálisan vagy aromatikusan.

⚠️ Fontos: Minden olaj kizárólag külső használatra. Soha ne fogyassz belsőleg professzionális útmutatás nélkül.

Szeretettel,
Soul Aligned Oils 💜"""
                else:
                    message = f"""🌙 Good Morning

Today {selected_primary or 'your oils'} and {selected_alternative or 'your alternative'} accompany you on your path.

🌿 Your Oil Companions for Today:
- {selected_primary or 'Primary Oil'}: Supports you in today's energy
- Alternative: {selected_alternative or 'Alternative Oil'}: A wonderful complement

✨ Your Ritual:
Take a moment for yourself and use the oils topically or aromatically.

⚠️ Important: All oils are for external use only. Never ingest without professional guidance.

With love,
Soul Aligned Oils 💜"""
            
            # Add safety disclaimer to every message
            safety_disclaimer = ""
            if language == 'de':
                safety_disclaimer = "\n\n⚠️ Wichtig: Alle Öle sind ausschließlich für externe Anwendung. Niemals ohne professionelle Anleitung einnehmen."
            elif language == 'hu':
                safety_disclaimer = "\n\n⚠️ Fontos: Minden olaj kizárólag külső használatra. Soha ne fogyassz belsőleg professzionális útmutatás nélkül."
            else:
                safety_disclaimer = "\n\n⚠️ Important: All oils are for external use only. Never ingest essential oils without professional guidance."
            
            message = message + safety_disclaimer
            
            logger.info(f"Successfully generated daily message in {language} (type: {message_type})")
            
            # Return message along with selected oils for database storage
            return {
                'message': message,
                'primary_oil': selected_primary,
                'alternative_oil': selected_alternative
            }
            
        except Exception as e:
            logger.error(f"Error generating affirmation: {e}", exc_info=True)
            return None
    
    def _create_prompt(self, language: str = 'en', exclude_oils: List[str] = None, 
                      selected_primary: str = None, selected_alternative: str = None) -> str:
        """Create the GPT prompt for generating the daily message."""
        day_name, month_name, date_string, day_energy, month_info = self._get_current_day_info()
        season = self._get_current_season()
        seasonal_oils = self.SEASONAL_OILS.get(season, [])
        oil_list = self._get_oil_list_string(exclude_oils)
        common_oils_str = ', '.join(self.COMMONLY_USED_OILS[:15])  # First 15 for brevity
        
        if language == 'de':
            return self._create_german_prompt(day_name, month_name, date_string, day_energy, month_info, oil_list, season, seasonal_oils, common_oils_str, selected_primary, selected_alternative)
        elif language == 'hu':
            return self._create_hungarian_prompt(day_name, month_name, date_string, day_energy, month_info, oil_list, season, seasonal_oils, common_oils_str, selected_primary, selected_alternative)
        else:
            return self._create_english_prompt(day_name, month_name, date_string, day_energy, month_info, oil_list, season, seasonal_oils, common_oils_str, selected_primary, selected_alternative)
    
    def _get_oil_list_string(self, exclude_oils: List[str] = None) -> str:
        """Create a formatted string of available oils for the prompt."""
        if exclude_oils is None:
            exclude_oils = []
        
        oil_strings = []
        for oil in self.oils:
            if oil['name'] not in exclude_oils:
                properties = ', '.join(oil['properties'][:4])
                oil_strings.append(f"- {oil['name']} ({properties})")
        return '\n'.join(oil_strings)
    
    def _create_portal_prompt(self, language: str, special_day_info: Dict, common_oils_str: str, 
                             exclude_oils: List[str] = None, selected_primary: str = None, selected_alternative: str = None) -> str:
        """Create prompt for portal days."""
        if exclude_oils is None:
            exclude_oils = []
        
        exclude_note = ""
        if exclude_oils:
            exclude_list = ', '.join(exclude_oils[:5])  # Show first 5
            if language == 'de':
                exclude_note = f"\n\nWICHTIG: Vermeide diese kürzlich verwendeten Öle: {exclude_list}"
            elif language == 'hu':
                exclude_note = f"\n\nFONTOS: Kerüld ezeket a nemrég használt olajokat: {exclude_list}"
            else:
                exclude_note = f"\n\nIMPORTANT: Avoid these recently used oils: {exclude_list}"
        
        # Enhanced with warmer, smarter tone
        if language == 'de':
            return f"""Heute ist ein besonderer Portaltag mit erhöhter Energie! ✨

Erstelle eine WARMHERZIGE, EINFÜHLSAME Nachricht auf DEUTSCH, die:
- Die besondere Energie dieses Tages respektiert und würdigt
- Erdung und Schutz als sanfte Unterstützung anbietet
- Transformation als natürlichen Prozess darstellt
- Sich anfühlt wie eine vertrauensvolle Begleitung

Empfohlene Öle: Vetiver, Balance, Peace & Calming, Frankincense{exclude_note}

STRUKTUR:

✨ Portaltag - Guten Morgen

[2-3 Sätze - warm, einfühlsam, die besondere Energie dieses Tages würdigend. 
Sprich über Erdung und Schutz als sanfte Unterstützung, nicht als Warnung. 
Sei ermutigend und präsent.]

🌿 Deine Öl-Begleiter:
{f"- {selected_primary}: [Ein warmer, persönlicher Satz - wie es sich anfühlt, dich zu erden und zu schützen]" if selected_primary else "- [Haupt-Öl Name]: [Ein warmer Satz über Erdung/Schutz]"}
{f"- Alternativ: {selected_alternative}: [Ein warmer, persönlicher Satz über den Nutzen]" if selected_alternative else "- Alternativ: [Alternatives Öl Name]: [Ein warmer Satz]"}

{"⚠️ WICHTIG: Verwende GENAU diese beiden Öle: {selected_primary} und {selected_alternative}. Öl-Namen IMMER auf ENGLISCH!" if selected_primary and selected_alternative else f"WICHTIG: Verwende eines dieser häufig verwendeten Öle: {common_oils_str}. ÖL-NAMEN IMMER AUF ENGLISCH!"}

✨ Dein Ritual:
[1-2 Sätze - eine sanfte, einladende Anleitung für Erdung und Selbstfürsorge. 
Formuliere es als freundliche Einladung zur Selbstpflege.]

💡 Für mehr Details: "Info [Haupt-Öl Name]" oder "Info [Alternatives Öl Name]"
🔄 Wiederholung: "Repeat [Zeit]" (z.B. "Repeat 14:30")

Mit Liebe, Soul Aligned Oils 💜"""
        elif language == 'en':
            return f"""Today is a special Portal Day with heightened energy! ✨

Create a WARM, EMPATHETIC message in English that:
- Honors and acknowledges the special energy of this day
- Offers grounding and protection as gentle support
- Presents transformation as a natural process
- Feels like trusted companionship

Recommended oils: Vetiver, Balance, Peace & Calming, Frankincense{exclude_note}

STRUCTURE:

✨ Portal Day - Good Morning

[2-3 sentences - warm, empathetic, honoring the special energy of this day.
Speak about grounding and protection as gentle support, not as a warning.
Be encouraging and present.]

🌿 Your Oil Companions:
{f"- {selected_primary}: [A warm, personal sentence - how it feels to ground and protect you]" if selected_primary else "- [Primary Oil Name]: [A warm sentence about grounding/protection]"}
{f"- Alternative: {selected_alternative}: [A warm, personal sentence about the benefit]" if selected_alternative else "- Alternative: [Alternative Oil Name]: [A warm sentence]"}

{"⚠️ IMPORTANT: Use EXACTLY these two oils: {selected_primary} and {selected_alternative}. Oil names ALWAYS in English!" if selected_primary and selected_alternative else f"IMPORTANT: Use one of these commonly used oils: {common_oils_str}. Oil names ALWAYS in English!"}

✨ Your Ritual:
[1-2 sentences - a gentle, inviting instruction for grounding and self-care.
Frame it as a friendly invitation to self-nurturing.]

💡 For more details: "Info [Primary Oil Name]" or "Info [Alternative Oil Name]"
🔄 Repeat message: "Repeat [time]" (e.g. "Repeat 14:30")

With love, Soul Aligned Oils 💜"""
        elif language == 'hu':
            return f"""FONTOS: Ma egy Portál nap fokozott energiával!

Hozz létre egy RÖVID üzenetet MAGYARUL, amely a következőkre összpontosít:
- Földelés és védelem
- Gyengéd öngondoskodás
- Transzformáció

Ajánlott olajok: Vetiver, Balance, Peace & Calming, Frankincense{exclude_note}

STRUKTÚRA:
✨ Portál nap - Jó reggelt

[2-3 mondat a földelésről és védelemről ezen a különleges napon]

🌿 Mai illóolaj társaid:
{f"- {selected_primary}: [Előny]" if selected_primary else "- [Fő olaj neve]: [Előny]"}
{f"- Alternatíva: {selected_alternative}: [Előny]" if selected_alternative else "- Alternatíva: [Alternatív olaj neve A GYAKRAN HASZNÁLT OLAJOKBÓL]: [Előny]"}

{"⚠️ KRITIKUS: Ezt a két olajat KELL használnod: {selected_primary} (Fő) és {selected_alternative} (Alternatív). NINCSEN más olaj! Az olajneveknek PONTOSAN ANGOLUL kell lenniük, ahogy itt van - SOHA ne fordítsd le!" if selected_primary and selected_alternative else f"FONTOS AZ ALTERNATÍV OLAJHOZ: MINDIG használj egyet ezekből a gyakran használt olajokból: {common_oils_str}. OLAJNEVEK MINDIG ANGOLUL!"}

✨ A te rituáléd:
[Egyszerű instrukció]

💡 További részletekért: "Info [Fő olaj neve]" vagy "Info [Alternatív olaj neve]"
🔄 Üzenet ismétlés: "Repeat [idő]" (pl. "Repeat 14:30" - példa idő, bármilyen időre beállítható 23:59-ig)

Szeretettel, Soul Aligned Oils 💜"""
        else:
            return """IMPORTANT: Today is a Portal Day with heightened energy!

Create a SHORT message focused on:
- Grounding and protection
- Gentle self-care
- Transformation

[Follow same structure as English]"""
    
    def _create_full_moon_prompt(self, language: str, special_day_info: Dict, common_oils_str: str, 
                                exclude_oils: List[str] = None, selected_primary: str = None, selected_alternative: str = None) -> str:
        """Create prompt for full moon days."""
        if exclude_oils is None:
            exclude_oils = []
        
        exclude_note = ""
        if exclude_oils:
            exclude_list = ', '.join(exclude_oils[:5])  # Show first 5
            if language == 'de':
                exclude_note = f"\n\nWICHTIG: Vermeide diese kürzlich verwendeten Öle: {exclude_list}"
            elif language == 'hu':
                exclude_note = f"\n\nFONTOS: Kerüld ezeket a nemrég használt olajokat: {exclude_list}"
            else:
                exclude_note = f"\n\nIMPORTANT: Avoid these recently used oils: {exclude_list}"
        
        if language == 'de':
            return f"""WICHTIG: Heute ist Vollmond! 🌕

Erstelle eine KURZE Nachricht auf DEUTSCH mit Fokus auf:
- Loslassen und Befreiung
- Manifestation
- Dankbarkeit

Empfohlene Öle: Lavender, Clary Sage, Ylang Ylang, Bergamot{exclude_note}

STRUKTUR:
🌕 Vollmond - Guten Morgen

[2-3 Sätze über Loslassen und Manifestation]

🌿 Deine Öl-Begleiter:
{f"- {selected_primary}: [Nutzen]" if selected_primary else "- [Haupt-Öl Name]: [Nutzen]"}
{f"- Alternativ: {selected_alternative}: [Nutzen]" if selected_alternative else "- Alternativ: [Alternatives Öl Name AUS DEN HÄUFIG VERWENDETEN ÖLEN]: [Nutzen]"}

{"⚠️ KRITISCH: Du MUSST diese beiden Öle verwenden: {selected_primary} und {selected_alternative}. KEINE anderen Öle! Die Öl-Namen müssen GENAU so auf ENGLISCH geschrieben werden - NIE übersetzen!" if selected_primary and selected_alternative else f"WICHTIG FÜR ALTERNATIVES ÖL: Verwende IMMER eines dieser häufig verwendeten Öle: {common_oils_str}. ÖL-NAMEN IMMER AUF ENGLISCH!"}

✨ Dein Ritual:
[Einfache Anleitung]

💡 Für mehr Details: "Info [Haupt-Öl Name]" oder "Info [Alternatives Öl Name]"
🔄 Wiederholung: "Repeat [Zeit]" (z.B. "Repeat 14:30" - Beispielzeit, kann auf beliebige Zeit bis 23:59 eingestellt werden)

Mit Liebe, Soul Aligned Oils 💜"""
        elif language == 'en':
            return f"""IMPORTANT: Today is Full Moon! 🌕

Create a SHORT message in English focused on:
- Release and liberation
- Manifestation
- Gratitude

Recommended oils: Lavender, Clary Sage, Ylang Ylang, Bergamot{exclude_note}

STRUCTURE:
🌕 Full Moon - Good Morning

[2-3 sentences about release and manifestation]

🌿 Your Oil Companions:
{f"- {selected_primary}: [Benefit]" if selected_primary else "- [Primary Oil Name]: [Benefit]"}
{f"- Alternative: {selected_alternative}: [Benefit]" if selected_alternative else "- Alternative: [Alternative Oil Name FROM COMMONLY USED OILS]: [Benefit]"}

{"⚠️ CRITICAL: You MUST use these two oils EXACTLY as written: {selected_primary} and {selected_alternative}. NO other oils! Use the EXACT English doTerra names - never translate or modify!" if selected_primary and selected_alternative else f"IMPORTANT FOR ALTERNATIVE OIL: ALWAYS use one of these commonly used oils: {common_oils_str}. Use EXACT English doTerra names."}

✨ Your Ritual:
[Simple instruction]

💡 For more details: "Info [Primary Oil Name]" or "Info [Alternative Oil Name]"
🔄 Repeat message: "Repeat [time]" (e.g. "Repeat 14:30" - example time, you can set any time until 23:59)

With love, Soul Aligned Oils 💜"""
        elif language == 'hu':
            return f"""FONTOS: Ma Telihold van! 🌕

Hozz létre egy RÖVID üzenetet MAGYARUL, amely a következőkre összpontosít:
- Elengedés és felszabadulás
- Megnyilvánulás
- Háláság

Ajánlott olajok: Lavender, Clary Sage, Ylang Ylang, Bergamot{exclude_note}

STRUKTÚRA:
🌕 Telihold - Jó reggelt

[2-3 mondat az elengedésről és megnyilvánulásról]

🌿 Mai illóolaj társaid:
{f"- {selected_primary}: [Előny]" if selected_primary else "- [Fő olaj neve]: [Előny]"}
{f"- Alternatíva: {selected_alternative}: [Előny]" if selected_alternative else "- Alternatíva: [Alternatív olaj neve A GYAKRAN HASZNÁLT OLAJOKBÓL]: [Előny]"}

{"⚠️ KRITIKUS: Ezt a két olajat KELL használnod: {selected_primary} (Fő) és {selected_alternative} (Alternatív). NINCSEN más olaj! Az olajneveknek PONTOSAN ANGOLUL kell lenniük, ahogy itt van - SOHA ne fordítsd le!" if selected_primary and selected_alternative else f"FONTOS AZ ALTERNATÍV OLAJHOZ: MINDIG használj egyet ezekből a gyakran használt olajokból: {common_oils_str}. OLAJNEVEK MINDIG ANGOLUL!"}

✨ A te rituáléd:
[Egyszerű instrukció]

💡 További részletekért: "Info [Fő olaj neve]" vagy "Info [Alternatív olaj neve]"
🔄 Üzenet ismétlés: "Repeat [idő]" (pl. "Repeat 14:30" - példa idő, bármilyen időre beállítható 23:59-ig)

Szeretettel, Soul Aligned Oils 💜"""
        else:
            return """IMPORTANT: Today is Full Moon! 🌕

Create a SHORT message about release and manifestation."""
    
    def _create_new_moon_prompt(self, language: str, special_day_info: Dict, common_oils_str: str, 
                               exclude_oils: List[str] = None, selected_primary: str = None, selected_alternative: str = None) -> str:
        """Create prompt for new moon days."""
        if exclude_oils is None:
            exclude_oils = []
        
        exclude_note = ""
        if exclude_oils:
            exclude_list = ', '.join(exclude_oils[:5])  # Show first 5
            if language == 'de':
                exclude_note = f"\n\nWICHTIG: Vermeide diese kürzlich verwendeten Öle: {exclude_list}"
            elif language == 'hu':
                exclude_note = f"\n\nFONTOS: Kerüld ezeket a nemrég használt olajokat: {exclude_list}"
            else:
                exclude_note = f"\n\nIMPORTANT: Avoid these recently used oils: {exclude_list}"
        
        if language == 'de':
            return f"""WICHTIG: Heute ist Neumond! 🌑

Erstelle eine KURZE Nachricht auf DEUTSCH mit Fokus auf:
- Neue Anfänge und Absichten
- Pflanzung von Samen
- Frische Energie

Empfohlene Öle: Frankincense, Sandalwood, Cedarwood, Balance{exclude_note}

STRUKTUR:
🌑 Neumond - Guten Morgen

[2-3 Sätze über neue Anfänge]

🌿 Deine Öl-Begleiter:
{f"- {selected_primary}: [Nutzen]" if selected_primary else "- [Haupt-Öl Name]: [Nutzen]"}
{f"- Alternativ: {selected_alternative}: [Nutzen]" if selected_alternative else "- Alternativ: [Alternatives Öl Name AUS DEN HÄUFIG VERWENDETEN ÖLEN]: [Nutzen]"}

{"⚠️ KRITISCH: Du MUSST diese beiden Öle verwenden: {selected_primary} und {selected_alternative}. KEINE anderen Öle! Die Öl-Namen müssen GENAU so auf ENGLISCH geschrieben werden - NIE übersetzen!" if selected_primary and selected_alternative else f"WICHTIG FÜR ALTERNATIVES ÖL: Verwende IMMER eines dieser häufig verwendeten Öle: {common_oils_str}. ÖL-NAMEN IMMER AUF ENGLISCH!"}

✨ Dein Ritual:
[Einfache Anleitung]

💡 Für mehr Details: "Info [Haupt-Öl Name]" oder "Info [Alternatives Öl Name]"
🔄 Wiederholung: "Repeat [Zeit]" (z.B. "Repeat 14:30" - Beispielzeit, kann auf beliebige Zeit bis 23:59 eingestellt werden)

Mit Liebe, Soul Aligned Oils 💜"""
        elif language == 'en':
            return f"""IMPORTANT: Today is New Moon! 🌑

Create a SHORT message in English focused on:
- New beginnings and intentions
- Planting seeds
- Fresh energy

Recommended oils: Frankincense, Sandalwood, Cedarwood, Balance{exclude_note}

STRUCTURE:
🌑 New Moon - Good Morning

[2-3 sentences about new beginnings]

🌿 Your Oil Companions:
{f"- {selected_primary}: [Benefit]" if selected_primary else "- [Primary Oil Name]: [Benefit]"}
{f"- Alternative: {selected_alternative}: [Benefit]" if selected_alternative else "- Alternative: [Alternative Oil Name FROM COMMONLY USED OILS]: [Benefit]"}

{"⚠️ CRITICAL: You MUST use these two oils EXACTLY as written: {selected_primary} and {selected_alternative}. NO other oils! Use the EXACT English doTerra names - never translate or modify!" if selected_primary and selected_alternative else f"IMPORTANT FOR ALTERNATIVE OIL: ALWAYS use one of these commonly used oils: {common_oils_str}. Use EXACT English doTerra names."}

✨ Your Ritual:
[Simple instruction]

💡 For more details: "Info [Primary Oil Name]" or "Info [Alternative Oil Name]"
🔄 Repeat message: "Repeat [time]" (e.g. "Repeat 14:30" - example time, you can set any time until 23:59)

With love, Soul Aligned Oils 💜"""
        elif language == 'hu':
            return f"""FONTOS: Ma Újhold van! 🌑

Hozz létre egy RÖVID üzenetet MAGYARUL, amely a következőkre összpontosít:
- Új kezdetek és szándékok
- Magok ültetése
- Friss energia

Ajánlott olajok: Frankincense, Sandalwood, Cedarwood, Balance{exclude_note}

STRUKTÚRA:
🌑 Újhold - Jó reggelt

[2-3 mondat az új kezdetekről]

🌿 Mai illóolaj társaid:
{f"- {selected_primary}: [Előny]" if selected_primary else "- [Fő olaj neve]: [Előny]"}
{f"- Alternatíva: {selected_alternative}: [Előny]" if selected_alternative else "- Alternatíva: [Alternatív olaj neve A GYAKRAN HASZNÁLT OLAJOKBÓL]: [Előny]"}

{"⚠️ KRITIKUS: Ezt a két olajat KELL használnod: {selected_primary} (Fő) és {selected_alternative} (Alternatív). NINCSEN más olaj! Az olajneveknek PONTOSAN ANGOLUL kell lenniük, ahogy itt van - SOHA ne fordítsd le!" if selected_primary and selected_alternative else f"FONTOS AZ ALTERNATÍV OLAJHOZ: MINDIG használj egyet ezekből a gyakran használt olajokból: {common_oils_str}. OLAJNEVEK MINDIG ANGOLUL!"}

✨ A te rituáléd:
[Egyszerű instrukció]

💡 További részletekért: "Info [Fő olaj neve]" vagy "Info [Alternatív olaj neve]"
🔄 Üzenet ismétlés: "Repeat [idő]" (pl. "Repeat 14:30" - példa idő, bármilyen időre beállítható 23:59-ig)

Szeretettel, Soul Aligned Oils 💜"""
        else:
            return """IMPORTANT: Today is New Moon! 🌑

Create a SHORT message about new beginnings."""
    
    def _create_german_prompt(self, day_name: str, month_name: str, date_string: str, 
                             day_energy: dict, month_info: dict, oil_list: str,
                             season: str, seasonal_oils: List[str], common_oils_str: str,
                             selected_primary: str = None, selected_alternative: str = None) -> str:
        """Create German version of the prompt - SHORT and PRACTICAL."""
        day_names_de = {
            'Monday': 'Montag', 'Tuesday': 'Dienstag', 'Wednesday': 'Mittwoch',
            'Thursday': 'Donnerstag', 'Friday': 'Freitag', 'Saturday': 'Samstag', 'Sunday': 'Sonntag'
        }
        month_names_de = {
            'January': 'Januar', 'February': 'Februar', 'March': 'März', 'April': 'April',
            'May': 'Mai', 'June': 'Juni', 'July': 'Juli', 'August': 'August',
            'September': 'September', 'October': 'Oktober', 'November': 'November', 'December': 'Dezember'
        }
        planet_names_de = {
            'Moon': 'Mond', 'Mars': 'Mars', 'Mercury': 'Merkur', 'Jupiter': 'Jupiter',
            'Venus': 'Venus', 'Saturn': 'Saturn', 'Sun': 'Sonne'
        }
        season_names_de = {
            'winter': 'Winter', 'spring': 'Frühling', 'summer': 'Sommer', 'autumn': 'Herbst'
        }
        
        day_name_de = day_names_de.get(day_name, day_name)
        month_name_de = month_names_de.get(month_name, month_name)
        planet_de = planet_names_de.get(day_energy['planet'], day_energy['planet'])
        season_de = season_names_de.get(season, season)
        
        seasonal_oils_str = ', '.join(seasonal_oils[:5]) if seasonal_oils else ''
        
        return f"""WICHTIG: Antworte AUSSCHLIESSLICH auf DEUTSCH! KURZ und PRAKTISCH!

Du bist ein ganzheitlicher Wellness-Guide. Erstelle eine KURZE, PRAKTISCHE Nachricht auf DEUTSCH.

HEUTE: {day_name_de} ({planet_de}-Energie) - {date_string}
Wochentag-Thema: {day_energy['theme']}
Wochentag-Fokus: {day_energy['focus']}

MONAT: {month_name_de} - {month_info['theme']}
JAHRESZEIT: {season_de}
Passende Öle für {season_de}: {seasonal_oils_str}

KRITISCHE ANFORDERUNGEN:
1. KURZ HALTEN - Maximal 3-4 kurze Absätze
2. PRAKTISCH - Muss in den Alltag passen
3. ZWEI ÖLE - Haupt + Alternative Empfehlung (bevorzuge {season_de}-Öle wenn passend)
4. EINFACHES RITUAL - Maximal 1-2 Sätze

STRUKTUR (EXAKT befolgen, komplett auf DEUTSCH):

🌙 Guten Morgen

[2-3 Sätze Affirmation verbunden mit der {day_name_de}-{planet_de}-Energie: {day_energy['theme']}]

🌿 Deine Öl-Begleiter für heute:
{f"- {selected_primary}: [EIN Satz Nutzen für die heutige Energie]" if selected_primary else "- [Haupt-Öl Name]: [EIN Satz Nutzen für die heutige Energie]"}
{f"- Alternativ: {selected_alternative}: [EIN Satz Nutzen]" if selected_alternative else "- Alternativ: [Alternatives Öl Name AUS DEN HÄUFIG VERWENDETEN ÖLEN]: [EIN Satz Nutzen]"}

{"⚠️ KRITISCH: Du MUSST diese beiden Öle verwenden: {selected_primary} (Haupt) und {selected_alternative} (Alternativ). KEINE anderen Öle!" if selected_primary and selected_alternative else f"WICHTIG FÜR ALTERNATIVES ÖL: Verwende IMMER eines dieser häufig verwendeten Öle: {common_oils_str}"}

✨ Dein Ritual:
[1-2 Sätze mit einfacher, umsetzbarer Anleitung]

💡 Für mehr Details: "Info [Haupt-Öl Name]" oder "Info [Alternatives Öl Name]"
🔄 Wiederholung: "Repeat [Zeit]" (z.B. "Repeat 14:30" - Beispielzeit, kann auf beliebige Zeit bis 23:59 eingestellt werden)

Mit Liebe,
Soul Aligned Oils 💜

VERFÜGBARE ÖLE:
{oil_list}

WICHTIG:
- Maximal 3-4 kurze Absätze insgesamt
- Affirmation: 2-3 Sätze, abgestimmt auf {day_name_de}s {planet_de}-Energie
- ZWEI Öle die zum {day_name_de}-Thema passen: {day_energy['theme']}
- Bevorzuge {season_de}-Öle wenn sie zum Thema passen
- Öl-Nutzen: JE EIN Satz
- Ritual: 1-2 Sätze, einfach und machbar
- Emojis NUR wie in der Struktur gezeigt
- Ton warm aber PRÄGNANT
- Die GESAMTE Nachricht auf DEUTSCH
- KEINE englischen Wörter außer "Soul Aligned Oils"
- ÖL-NAMEN: IMMER auf ENGLISCH (originale doTerra-Namen wie "Lavender", "Frankincense", etc.) - NIE übersetzen!
"""
    
    def _create_english_prompt(self, day_name: str, month_name: str, date_string: str, 
                              day_energy: dict, month_info: dict, oil_list: str,
                              season: str, seasonal_oils: List[str], common_oils_str: str,
                              selected_primary: str = None, selected_alternative: str = None) -> str:
        """Create English version of the prompt - SHORT and PRACTICAL."""
        seasonal_oils_str = ', '.join(seasonal_oils[:5]) if seasonal_oils else ''
        
        return f"""Create a WARM, EMPATHETIC daily affirmation in English.

CONTEXT FOR TODAY:
📅 {day_name} ({day_energy['planet']} Energy) - {date_string}
💫 Day Energy: {day_energy['theme']}
🎯 Focus: {day_energy['focus']}
📆 Month: {month_name} - {month_info['theme']}
🌿 Season: {season}

YOUR TASK:
Create a message that feels like a warm conversation with a trusted friend.
The affirmation should:
- EMOTIONALLY resonate and feel authentic
- Be PRACTICAL and fit naturally into daily life
- INTELLIGENTLY use today's energy
- Flow NATURALLY, not feel stiff or robotic
- Stay SHORT (3-4 paragraphs) but still be substantial

STRUCTURE:

🌙 Good Morning

[2-3 sentences affirmation - warm, personal, connected to {day_name}'s {day_energy['planet']} energy.
Speak directly to the person, be empathetic and encouraging. Use the energy of {day_energy['theme']} 
and weave it together with {month_info['theme']}.]

🌿 Your Oil Companions for Today:
{f"- {selected_primary}: [A warm, personal sentence about the benefit - how it feels, not just what it does]" if selected_primary else "- [Primary Oil Name]: [A warm sentence about the benefit]"}
{f"- Alternative: {selected_alternative}: [A warm, personal sentence about the benefit]" if selected_alternative else "- Alternative: [Alternative Oil Name]: [A warm sentence about the benefit]"}

{"⚠️ IMPORTANT: Use EXACTLY these two oils: {selected_primary} (Primary) and {selected_alternative} (Alternative). Oil names ALWAYS in English!" if selected_primary and selected_alternative else ""}

✨ Your Ritual:
[1-2 sentences - a simple, inviting instruction that feels good and is easy to implement.
Frame it as a friendly invitation, not a command.]

💡 For more details: "Info [Primary Oil Name]" or "Info [Alternative Oil Name]"
🔄 Repeat message: "Repeat [time]" (e.g. "Repeat 14:30" - example time, you can set any time until 23:59)

With love,
Soul Aligned Oils 💜

AVAILABLE OILS:
{oil_list}

IMPORTANT FOR TONE:
- Write like a trusted friend who truly listens and understands
- Be warm but not overdone - authentic and real
- Use the energy of {day_energy['theme']} intelligently, not mechanically
- Weave {month_info['theme']} naturally with today's energy
- Frame oil benefits personally: "How it feels" rather than just "What it does"
- Ritual as friendly invitation, not obligation
- Maximum 3-4 paragraphs, but every line should have meaning
- Oil names ALWAYS in English (original doTerra names)
"""
    
    def _create_hungarian_prompt(self, day_name: str, month_name: str, date_string: str, 
                                day_energy: dict, month_info: dict, oil_list: str,
                                season: str, seasonal_oils: List[str], common_oils_str: str,
                                selected_primary: str = None, selected_alternative: str = None) -> str:
        """Create Hungarian version of the prompt - SHORT and PRACTICAL."""
        # Hungarian translations for day and month names
        day_names_hu = {
            'Monday': 'Hétfő', 'Tuesday': 'Kedd', 'Wednesday': 'Szerda',
            'Thursday': 'Csütörtök', 'Friday': 'Péntek', 'Saturday': 'Szombat', 'Sunday': 'Vasárnap'
        }
        month_names_hu = {
            'January': 'Január', 'February': 'Február', 'March': 'Március', 'April': 'Április',
            'May': 'Május', 'June': 'Június', 'July': 'Július', 'August': 'Augusztus',
            'September': 'Szeptember', 'October': 'Október', 'November': 'November', 'December': 'December'
        }
        planet_names_hu = {
            'Moon': 'Hold', 'Mars': 'Mars', 'Mercury': 'Merkúr', 'Jupiter': 'Jupiter',
            'Venus': 'Vénusz', 'Saturn': 'Szaturnusz', 'Sun': 'Nap'
        }
        season_names_hu = {
            'winter': 'Tél', 'spring': 'Tavasz', 'summer': 'Nyár', 'autumn': 'Ősz'
        }
        
        day_name_hu = day_names_hu.get(day_name, day_name)
        month_name_hu = month_names_hu.get(month_name, month_name)
        planet_hu = planet_names_hu.get(day_energy['planet'], day_energy['planet'])
        season_hu = season_names_hu.get(season, season)
        
        seasonal_oils_str = ', '.join(seasonal_oils[:5]) if seasonal_oils else ''
        
        return f"""Hozz létre egy MELEG, EGYÜTTÉRZŐ napi megerősítést MAGYARUL.

KONTEXTUS MA:
📅 {day_name_hu} ({planet_hu} Energia) - {date_string}
💫 Nap energiája: {day_energy['theme']}
🎯 Fókusz: {day_energy['focus']}
📆 Hónap: {month_name_hu} - {month_info['theme']}
🌿 Évszak: {season_hu}

A FELADATOD:
Hozz létre egy üzenetet, ami úgy érződik, mintha egy megbízható barátnővel beszélnél.
A megerősítésnek:
- ÉRZELMILEG rezonálnia kell és autentikusnak kell érződnie
- GYAKORLATINAK kell lennie és természetesen illeszkednie a mindennapi életbe
- OKOSAN használnia kell a mai energiát
- TERMÉSZETESEN kell folynia, ne mereven vagy robotikusan
- RÖVIDEN kell maradnia (3-4 bekezdés), de mégis lényegretörőnek

STRUKTÚRA:

🌙 Jó reggelt

[2-3 mondatos megerősítés - meleg, személyes, kapcsolódva a {day_name_hu} {planet_hu} energiájához.
Közvetlenül beszélj a személyhez, légy együttérző és bátorító. Használd a {day_energy['theme']} 
energiáját és fonjad össze a {month_info['theme']} témával.]

🌿 Mai illóolaj társaid:
{f"- {selected_primary}: [Egy meleg, személyes mondat az előnyről - hogyan érződik, nem csak mit csinál]" if selected_primary else "- [Fő olaj neve]: [Egy meleg mondat az előnyről]"}
{f"- Alternatíva: {selected_alternative}: [Egy meleg, személyes mondat az előnyről]" if selected_alternative else "- Alternatíva: [Alternatív olaj neve]: [Egy meleg mondat az előnyről]"}

{"⚠️ FONTOS: Használd PONTOSAN ezt a két olajat: {selected_primary} (Fő) és {selected_alternative} (Alternatív). Olajnevek MINDIG ANGOLUL!" if selected_primary and selected_alternative else ""}

✨ A te rituáléd:
[1-2 mondat - egy egyszerű, meghívó instrukció, ami jól érződik és könnyen megvalósítható.
Fogalmazd meg barátságos meghívásként, ne parancsként.]

💡 További részletekért: "Info [Fő olaj neve]" vagy "Info [Alternatív olaj neve]"
🔄 Üzenet ismétlés: "Repeat [idő]" (pl. "Repeat 14:30" - példa idő, bármilyen időre beállítható 23:59-ig)

Szeretettel,
Soul Aligned Oils 💜

ELÉRHETŐ OLAJOK:
{oil_list}

FONTOS A HANGVÉTELHEZ:
- Írj úgy, mint egy megbízható barátnő, aki valóban hallgat és megért
- Légy meleg, de ne túlzásba - autentikus és valódi
- Használd a {day_energy['theme']} energiáját okosan, ne mechanikusan
- Fonjad össze a {month_info['theme']} témát természetesen a mai energiával
- Fogalmazd meg az olaj előnyöket személyesen: "Hogyan érződik" nem csak "Mit csinál"
- Rituálé barátságos meghívásként, ne kötelezettségként
- Maximum 3-4 bekezdés, de minden sor legyen értékes
- A TELJES üzenet MAGYARUL
- OLAJNEVEK: MINDIG ANGOLUL (eredeti doTerra nevek) - SOHA ne fordítsd le!
"""

