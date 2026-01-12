"""
Script to populate the oils database with detailed information.
Run this once to initialize the database with oil data.
"""

import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database
from config import Config

def populate_oils():
    """Populate oils database from JSON file."""
    db = Database()
    
    # Load oils from JSON
    with open(Config.OILS_DATABASE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    oils_data = data['oils']
    print(f"Populating database with {len(oils_data)} oils...")
    
    # Detailed oil information (extended from basic JSON)
    detailed_oils = {
        'Lavender': {
            'energetic_effects': 'Lavender wirkt beruhigend auf das emotionale Zentrum und fördert tiefe Entspannung. Es hilft beim Loslassen von Stress und unterstützt einen erholsamen Schlaf. Energetisch öffnet es das Herz für Selbstliebe und Mitgefühl.',
            'main_components': [
                {'name': 'Linalool', 'effect': 'Beruhigend und entspannend'},
                {'name': 'Linalyl Acetate', 'effect': 'Anti-Stress und harmonisierend'},
                {'name': 'Terpinen-4-ol', 'effect': 'Entzündungshemmend'}
            ],
            'interesting_facts': 'Lavendel wurde bereits in der Antike für seine beruhigenden Eigenschaften geschätzt. Der Name leitet sich vom lateinischen "lavare" (waschen) ab, da er traditionell für Bäder verwendet wurde.',
            'seasonal_fit': ['spring', 'summer', 'autumn'],
            'weekday_energy_match': ['Monday', 'Friday', 'Sunday'],
            'contraindications': 'Gilt als sehr sicher. Bei empfindlicher Haut mit Trägeröl verdünnen.',
            'best_uses': ['Topisch auf Schläfen und Handgelenken', 'Aromatisch im Diffuser vor dem Schlaf', 'Intern in Kapseln für Entspannung']
        },
        'Frankincense': {
            'energetic_effects': 'Weihrauch verbindet uns mit dem Spirituellen und fördert tiefe Erdung. Es öffnet das Kronen-Chakra und unterstützt Meditation und Gebet. Energetisch bringt es Frieden und spirituelle Weisheit.',
            'main_components': [
                {'name': 'Alpha-Pinene', 'effect': 'Entzündungshemmend und kognitive Unterstützung'},
                {'name': 'Limonene', 'effect': 'Stimmungsaufhellend'},
                {'name': 'Alpha-Thujene', 'effect': 'Zellschutz'}
            ],
            'interesting_facts': 'Weihrauch war eines der wertvollsten Geschenke, die die Heiligen Drei Könige dem Jesuskind brachten. Es wird seit über 5000 Jahren für spirituelle Zeremonien verwendet.',
            'seasonal_fit': ['winter', 'autumn'],
            'weekday_energy_match': ['Monday', 'Sunday'],
            'contraindications': 'Sehr sicher. Kann während der Schwangerschaft verwendet werden.',
            'best_uses': ['Topisch auf Handgelenken und über dem Herzen', 'Aromatisch während Meditation', 'Intern für zelluläre Unterstützung']
        },
        'Peppermint': {
            'energetic_effects': 'Pfefferminze bringt Klarheit und geistige Frische. Sie unterstützt Fokus und Konzentration und hilft bei mentaler Erschöpfung. Energetisch aktiviert sie das Solarplexus-Chakra für mehr Durchsetzungskraft.',
            'main_components': [
                {'name': 'Menthol', 'effect': 'Kühlend und erfrischend'},
                {'name': 'Menthon', 'effect': 'Entspannend'},
                {'name': 'Menthyl Acetate', 'effect': 'Beruhigend für Muskeln'}
            ],
            'interesting_facts': 'Pfefferminze ist eine natürliche Hybridpflanze aus Wasserminze und Grüner Minze. Sie wurde bereits im antiken Griechenland für ihre wohltuenden Eigenschaften geschätzt.',
            'seasonal_fit': ['spring', 'summer'],
            'weekday_energy_match': ['Tuesday', 'Wednesday'],
            'contraindications': 'Nicht bei Kindern unter 6 Jahren verwenden. Kann die Milchproduktion bei stillenden Müttern beeinflussen.',
            'best_uses': ['Topisch auf Nacken und Schläfen für Fokus', 'Direkt inhalieren für Energie', 'Intern in Wasser für Verdauung']
        },
        # Add more detailed oils as needed...
    }
    
    count = 0
    for oil in oils_data:
        oil_name = oil['name']
        
        # Check if we have detailed info
        detailed_info = detailed_oils.get(oil_name, {})
        
        # Build oil data structure
        oil_data = {
            'oil_name': oil_name,
            'alternative_names': [],  # Can be populated with German/English variations
            'energetic_effects': detailed_info.get('energetic_effects', 
                f"{oil_name} unterstützt dich energetisch durch seine natürlichen Eigenschaften: {', '.join(oil.get('properties', [])[:3])}."),
            'main_components': detailed_info.get('main_components', 
                [{'name': 'Natürliche Verbindungen', 'effect': 'Aus der Pflanze gewonnen'}]),
            'interesting_facts': detailed_info.get('interesting_facts',
                f"{oil_name} ist ein wertvolles ätherisches Öl mit vielen traditionellen Anwendungen."),
            'seasonal_fit': detailed_info.get('seasonal_fit', ['winter', 'spring', 'summer', 'autumn']),
            'weekday_energy_match': detailed_info.get('weekday_energy_match', ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']),
            'contraindications': detailed_info.get('contraindications', 'Als sicher erachtet. Bei empfindlicher Haut mit Trägeröl verdünnen.'),
            'best_uses': oil.get('usage_methods', ['topical', 'aromatic'])
        }
        
        # Add German alternative names for common oils
        german_names = {
            'Lavender': ['Lavendel'],
            'Peppermint': ['Pfefferminze'],
            'Frankincense': ['Weihrauch'],
            'Lemon': ['Zitrone'],
            'Orange': ['Orange'],
            'Bergamot': ['Bergamotte'],
            'Eucalyptus': ['Eukalyptus'],
            'Cedarwood': ['Zedernholz'],
            'Sandalwood': ['Sandelholz'],
            'Rosemary': ['Rosmarin'],
            'Cinnamon Bark': ['Zimtrinde', 'Zimt', 'Cinnamon'],
            'Ginger': ['Ingwer'],
            'Lavender': ['Lavendel'],
            'Clary Sage': ['Muskatellersalbei'],
            'Ylang Ylang': ['Ylang Ylang'],
            'Vetiver': ['Vetiver'],
            'Balance': ['Balance'],
            'Peace & Calming': ['Peace & Calming']
        }
        
        if oil_name in german_names:
            oil_data['alternative_names'] = german_names[oil_name]
        
        # Save to database
        if db.add_oil(oil_data):
            count += 1
            print(f"✓ Added {oil_name}")
        else:
            print(f"✗ Failed to add {oil_name}")
    
    print(f"\n✅ Successfully populated {count}/{len(oils_data)} oils in database!")
    return count

if __name__ == '__main__':
    print("=" * 70)
    print("POPULATING OILS DATABASE")
    print("=" * 70)
    print()
    
    try:
        count = populate_oils()
        print()
        print("=" * 70)
        print(f"DONE! {count} oils in database.")
        print("=" * 70)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
