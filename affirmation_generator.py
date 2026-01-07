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
        """Get current day information."""
        now = datetime.now()
        day_name = now.strftime('%A')
        date_string = now.strftime('%B %d, %Y')
        day_energy = self.DAY_ENERGY.get(day_name, 'Balance and presence')
        return day_name, date_string, day_energy
    
    def _create_prompt(self, language: str = 'en') -> str:
        """Create the GPT prompt for generating the daily message."""
        day_name, date_string, day_energy = self._get_current_day_info()
        oil_list = self._get_oil_list_string()
        
        if language == 'de':
            return self._create_german_prompt(day_name, date_string, day_energy, oil_list)
        else:
            return self._create_english_prompt(day_name, date_string, day_energy, oil_list)
    
    def _create_english_prompt(self, day_name: str, date_string: str, day_energy: str, oil_list: str) -> str:
        """Create English version of the prompt."""
        return f"""You are a holistic wellness guide specializing in essential oils and positive mindset coaching.

Today is {day_name}, {date_string}.

{day_name} energy characteristics:
{day_energy}

Generate a daily message with three components:

1. AFFIRMATION: Create a powerful, personal affirmation (2-3 sentences) that aligns with today's energy. Make it feel intimate, supportive, and emotionally resonant. Use "I" statements to make it personal.

2. OIL RECOMMENDATION: Select ONE doTerra essential oil from the provided list that energetically supports this affirmation. Explain briefly (1-2 sentences) why this oil matches today's intention and energy.

3. USAGE RITUAL: Provide a specific, mindful application method. Include where to apply, when to use it, and any additional instructions for aromatic or internal use if appropriate. Make it feel like a sacred ritual.

Format the response as a cohesive, flowing message that feels like a caring friend reaching out. Use the following structure:

🌅 Good Morning, Beautiful Soul

[Opening sentence about today being a day of...]

"[Personal affirmation in first person, 2-3 sentences]"

✨ Your Oil Companion: [Oil Name]
[Brief explanation of why this oil matches today's energy]

🌿 Your Ritual:
[Specific application instructions that feel mindful and intentional]

With love and light,
Soul Aligned Oils 💜

Available oils:
{oil_list}

Important: 
- Keep the tone warm, personal, and uplifting
- Make the affirmation feel powerful and believable
- Ensure the oil selection genuinely matches the theme
- Make the ritual instructions specific and actionable
- Use emojis sparingly but meaningfully (only the ones shown in the structure)
"""
    
    def _create_german_prompt(self, day_name: str, date_string: str, day_energy: str, oil_list: str) -> str:
        """Create German version of the prompt."""
        day_names_de = {
            'Monday': 'Montag', 'Tuesday': 'Dienstag', 'Wednesday': 'Mittwoch',
            'Thursday': 'Donnerstag', 'Friday': 'Freitag', 'Saturday': 'Samstag', 'Sunday': 'Sonntag'
        }
        day_name_de = day_names_de.get(day_name, day_name)
        
        return f"""WICHTIG: Antworte AUSSCHLIESSLICH auf DEUTSCH! Die GESAMTE Nachricht muss auf Deutsch sein!

Du bist ein ganzheitlicher Wellness-Guide, spezialisiert auf ätherische Öle und positive Lebenseinstellung.

Heute ist {day_name_de}, {date_string}.

{day_name} Energie-Eigenschaften:
{day_energy}

Erstelle eine tägliche Nachricht VOLLSTÄNDIG AUF DEUTSCH mit drei Komponenten:

1. AFFIRMATION: Erstelle eine kraftvolle, persönliche Affirmation (2-3 Sätze) auf DEUTSCH, die mit der heutigen Energie übereinstimmt. Sie soll intim, unterstützend und emotional berührend sein. Verwende "Ich"-Aussagen.

2. ÖL-EMPFEHLUNG: Wähle EIN doTerra ätherisches Öl aus der Liste. Erkläre auf DEUTSCH kurz (1-2 Sätze), warum dieses Öl zur heutigen Intention passt.

3. ANWENDUNGS-RITUAL: Gebe auf DEUTSCH eine spezifische, achtsame Anwendungsmethode. Erkläre, wo man es aufträgt und wie man es verwendet.

Verwende EXAKT diese Struktur (alles auf Deutsch):

🌅 Guten Morgen, Wunderschöne Seele

[Einleitungssatz auf Deutsch über den heutigen Tag]

"[Persönliche Affirmation auf Deutsch in Ich-Form, 2-3 Sätze]"

✨ Dein Öl-Begleiter: [Öl-Name]
[Kurze Erklärung auf Deutsch, warum dieses Öl passt]

🌿 Dein Ritual:
[Spezifische Anwendungsanweisungen auf Deutsch]

Mit Liebe und Licht,
Soul Aligned Oils 💜

Verfügbare Öle:
{oil_list}

KRITISCH WICHTIG: 
- Die GESAMTE Nachricht MUSS auf Deutsch sein
- KEINE englischen Wörter außer "Soul Aligned Oils" in der Signatur
- Halte den Ton warm, persönlich und erhebend
- Verwende natürliches, fließendes Deutsch
- Die Affirmation in Ich-Form auf Deutsch
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

