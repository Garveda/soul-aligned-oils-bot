"""
Affirmation Generator Module
Integrates with OpenAI API to generate personalized daily affirmations
with doTerra essential oil recommendations in multiple languages.
"""

import json
import logging
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
    
    def __init__(self):
        """Initialize the affirmation generator."""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.oils = self._load_oils()
        
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
    
    def _get_current_day_info(self) -> tuple:
        """Get current day and month information."""
        now = datetime.now()
        day_name = now.strftime('%A')
        month_name = now.strftime('%B')
        date_string = now.strftime('%B %d, %Y')
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
        
        return f"""WICHTIG: Antworte AUSSCHLIESSLICH auf DEUTSCH! KURZ und PRAKTISCH!

Du bist ein ganzheitlicher Wellness-Guide. Erstelle eine KURZE, PRAKTISCHE Nachricht auf DEUTSCH.

HEUTE: {day_name_de} ({planet_de}-Energie) - {date_string}
Wochentag-Thema: {day_energy['theme']}
Wochentag-Fokus: {day_energy['focus']}

MONAT: {month_name_de} - {month_info['theme']}

KRITISCHE ANFORDERUNGEN:
1. KURZ HALTEN - Maximal 3-4 kurze Absätze
2. PRAKTISCH - Muss in den Alltag passen
3. ZWEI ÖLE - Haupt + Alternative Empfehlung
4. EINFACHES RITUAL - Maximal 1-2 Sätze

STRUKTUR (EXAKT befolgen, komplett auf DEUTSCH):

🌙 Guten Morgen

[2-3 Sätze Affirmation verbunden mit der {day_name_de}-{planet_de}-Energie: {day_energy['theme']}]

🌿 Deine Öl-Begleiter für heute:
- [Haupt-Öl Name]: [EIN Satz Nutzen für die heutige Energie]
- Alternativ: [Alternatives Öl Name]: [EIN Satz Nutzen]

✨ Dein Ritual:
[1-2 Sätze mit einfacher, umsetzbarer Anleitung]

Mit Liebe,
Soul Aligned Oils 💜

VERFÜGBARE ÖLE:
{oil_list}

WICHTIG:
- Maximal 3-4 kurze Absätze insgesamt
- Affirmation: 2-3 Sätze, abgestimmt auf {day_name_de}s {planet_de}-Energie
- ZWEI Öle die zum {day_name_de}-Thema passen: {day_energy['theme']}
- Öl-Nutzen: JE EIN Satz
- Ritual: 1-2 Sätze, einfach und machbar
- Emojis NUR wie in der Struktur gezeigt
- Ton warm aber PRÄGNANT
- Die GESAMTE Nachricht auf DEUTSCH
- KEINE englischen Wörter außer "Soul Aligned Oils"
"""
    
    def generate_daily_message(self, language: str = 'en') -> Optional[str]:
        """Generate the complete daily affirmation message."""
        try:
            prompt = self._create_prompt(language)
            logger.info(f"Requesting affirmation from OpenAI API (language: {language})")
            
            # Customize system message based on language
            if language == 'de':
                system_content = "Du bist ein mitfühlender Wellness-Guide, der KURZE, PRAKTISCHE tägliche Affirmationen erstellt. WICHTIG: Antworte IMMER auf DEUTSCH. Halte die Nachricht KURZ und PRÄGNANT (maximal 3-4 Absätze). Schreibe die GESAMTE Nachricht auf Deutsch."
            else:
                system_content = "You are a compassionate wellness guide who creates SHORT, PRACTICAL daily affirmations. Keep messages BRIEF and CONCISE (maximum 3-4 paragraphs)."
            
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
            logger.info(f"Successfully generated daily message in {language}")
            return message
            
        except Exception as e:
            logger.error(f"Error generating affirmation: {e}", exc_info=True)
            return None

