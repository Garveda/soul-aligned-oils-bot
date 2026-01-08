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
    
    # Day energy characteristics
    DAY_ENERGY = {
        'Monday': 'New beginnings, fresh starts, intention setting, new chapter',
        'Tuesday': 'Action, momentum, courage, forward movement, determination',
        'Wednesday': 'Balance, reflection, midpoint recalibration, harmony, wisdom',
        'Thursday': 'Expansion, growth, gratitude, abundance, manifestation',
        'Friday': 'Release, completion, celebration, freedom, joy',
        'Saturday': 'Rest, self-care, rejuvenation, play, personal nourishment',
        'Sunday': 'Reflection, spiritual connection, preparation, inner peace, renewal'
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
        day_energy = self.DAY_ENERGY.get(day_name, 'Balance and presence')
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
    
    def _create_english_prompt(self, day_name: str, month_name: str, date_string: str, day_energy: str, month_info: dict, oil_list: str) -> str:
        """Create English version of the prompt."""
        return f"""You are a holistic wellness guide specializing in essential oils and positive mindset coaching.

Today is {day_name}, {date_string}.

MONTHLY THEME - {month_name}: {month_info['theme']}
Monthly Focus: {month_info['focus']}
Monthly Energy: {month_info['energy']}

DAILY ENERGY - {day_name}:
{day_energy}

IMPORTANT: Create an affirmation that weaves together BOTH the monthly theme of {month_name} ({month_info['theme']}) AND the daily energy of {day_name}. The affirmation should feel aligned with where we are in the year and what this specific day of the week brings.

Generate a daily message with three components:

1. AFFIRMATION: Create a powerful, personal affirmation (2-3 sentences) that INTEGRATES:
   - The monthly theme of {month_name} ({month_info['theme']})
   - The daily energy of {day_name} ({day_energy})
   Make it feel intimate, supportive, and emotionally resonant. Use "I" statements to make it personal.

2. OIL RECOMMENDATION: Select ONE doTerra essential oil from the provided list that energetically supports BOTH the monthly theme AND today's daily intention. Explain briefly (1-2 sentences) why this oil is perfect for this specific {day_name} in {month_name}.

3. USAGE RITUAL: Provide a specific, mindful application method that honors this moment in time. Make it feel like a sacred ritual aligned with the season and day.

Format the response as a cohesive, flowing message that feels like a caring friend reaching out. Use the following structure:

🌅 Good Morning, Beautiful Soul

[Opening sentence that mentions it's {day_name} in {month_name} and weaves together the monthly and daily themes]

"[Personal affirmation in first person that combines monthly + daily energy, 2-3 sentences]"

✨ Your Oil Companion: [Oil Name]
[Brief explanation of why this oil matches BOTH the {month_name} theme and {day_name} energy]

🌿 Your Ritual:
[Specific application instructions that feel mindful and intentional]

With love and light,
Soul Aligned Oils 💜

Available oils:
{oil_list}

Important: 
- Seamlessly blend the monthly theme with the daily energy
- Keep the tone warm, personal, and uplifting
- Make the affirmation feel powerful and believable
- Ensure the oil selection genuinely matches BOTH themes
- Make the ritual instructions specific and actionable
- Reference the time of year naturally in your message
- Use emojis sparingly but meaningfully (only the ones shown in the structure)
"""
    
    def _create_german_prompt(self, day_name: str, month_name: str, date_string: str, day_energy: str, month_info: dict, oil_list: str) -> str:
        """Create German version of the prompt."""
        day_names_de = {
            'Monday': 'Montag', 'Tuesday': 'Dienstag', 'Wednesday': 'Mittwoch',
            'Thursday': 'Donnerstag', 'Friday': 'Freitag', 'Saturday': 'Samstag', 'Sunday': 'Sonntag'
        }
        month_names_de = {
            'January': 'Januar', 'February': 'Februar', 'March': 'März', 'April': 'April',
            'May': 'Mai', 'June': 'Juni', 'July': 'Juli', 'August': 'August',
            'September': 'September', 'October': 'Oktober', 'November': 'November', 'December': 'Dezember'
        }
        day_name_de = day_names_de.get(day_name, day_name)
        month_name_de = month_names_de.get(month_name, month_name)
        
        return f"""WICHTIG: Antworte AUSSCHLIESSLICH auf DEUTSCH! Die GESAMTE Nachricht muss auf Deutsch sein!

Du bist ein ganzheitlicher Wellness-Guide, spezialisiert auf ätherische Öle und positive Lebenseinstellung.

Heute ist {day_name_de}, {date_string}.

MONATS-THEMA - {month_name_de}: {month_info['theme']}
Monatlicher Fokus: {month_info['focus']}
Monatliche Energie: {month_info['energy']}

TAGES-ENERGIE - {day_name_de}:
{day_energy}

WICHTIG: Erstelle eine Affirmation, die SOWOHL das Monatsthema des {month_name_de} ({month_info['theme']}) ALS AUCH die Tagesenergie des {day_name_de} miteinander verwebt. Die Affirmation soll sich stimmig anfühlen mit der Jahreszeit und diesem spezifischen Wochentag.

Erstelle eine tägliche Nachricht VOLLSTÄNDIG AUF DEUTSCH mit drei Komponenten:

1. AFFIRMATION: Erstelle eine kraftvolle, persönliche Affirmation (2-3 Sätze) auf DEUTSCH, die INTEGRIERT:
   - Das Monatsthema des {month_name_de} ({month_info['theme']})
   - Die Tagesenergie des {day_name_de} ({day_energy})
   Sie soll intim, unterstützend und emotional berührend sein. Verwende "Ich"-Aussagen.

2. ÖL-EMPFEHLUNG: Wähle EIN doTerra ätherisches Öl aus der Liste, das energetisch SOWOHL das Monatsthema ALS AUCH die heutige Tages-Intention unterstützt. Erkläre auf DEUTSCH kurz (1-2 Sätze), warum dieses Öl perfekt für diesen {day_name_de} im {month_name_de} ist.

3. ANWENDUNGS-RITUAL: Gebe auf DEUTSCH eine spezifische, achtsame Anwendungsmethode, die diesen Moment im Jahr ehrt. Lass es sich wie ein heiliges Ritual anfühlen, das zur Jahreszeit und zum Wochentag passt.

Verwende EXAKT diese Struktur (alles auf Deutsch):

🌅 Guten Morgen, Wunderschöne Seele

[Einleitungssatz auf Deutsch, der erwähnt dass es {day_name_de} im {month_name_de} ist und die Monats- und Tages-Themen miteinander verwebt]

"[Persönliche Affirmation auf Deutsch in Ich-Form, die monatliche + tägliche Energie kombiniert, 2-3 Sätze]"

✨ Dein Öl-Begleiter: [Öl-Name]
[Kurze Erklärung auf Deutsch, warum dieses Öl SOWOHL zum {month_name_de}-Thema ALS AUCH zur {day_name_de}-Energie passt]

🌿 Dein Ritual:
[Spezifische Anwendungsanweisungen auf Deutsch]

Mit Liebe und Licht,
Soul Aligned Oils 💜

Verfügbare Öle:
{oil_list}

KRITISCH WICHTIG: 
- Verwebe nahtlos das Monatsthema mit der Tagesenergie
- Die GESAMTE Nachricht MUSS auf Deutsch sein
- KEINE englischen Wörter außer "Soul Aligned Oils" in der Signatur
- Halte den Ton warm, persönlich und erhebend
- Verwende natürliches, fließendes Deutsch
- Die Affirmation in Ich-Form auf Deutsch
- Beziehe die Jahreszeit natürlich in deine Nachricht ein
"""
    
    def generate_daily_message(self, language: str = 'en') -> Optional[str]:
        """Generate the complete daily affirmation message."""
        try:
            prompt = self._create_prompt(language)
            logger.info(f"Requesting affirmation from OpenAI API (language: {language})")
            
            # Customize system message based on language
            if language == 'de':
                system_content = "Du bist ein mitfühlender Wellness-Guide, der bedeutungsvolle tägliche Affirmationen erstellt, die mit ätherischen Ölempfehlungen kombiniert werden. WICHTIG: Antworte IMMER auf DEUTSCH. Schreibe die GESAMTE Nachricht auf Deutsch."
            else:
                system_content = "You are a compassionate wellness guide who creates meaningful daily affirmations paired with essential oil recommendations."
            
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            message = response.choices[0].message.content.strip()
            logger.info(f"Successfully generated daily message in {language}")
            return message
            
        except Exception as e:
            logger.error(f"Error generating affirmation: {e}", exc_info=True)
            return None

