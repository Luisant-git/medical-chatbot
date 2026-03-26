# Translation module for English, Tamil, and Tanglish support

TRANSLATIONS = {
    'en': {
        'greeting': 'Hello! I\'m your medical diagnosis assistant. How can I help you today?',
        'symptom_prompt': 'Please describe your symptoms',
        'analyzing': 'Analyzing your symptoms...',
        'emergency': '🚨 EMERGENCY: Call 911 or go to ER immediately!',
        'location_denied': '📍 Location access denied. Doctor recommendations will be limited.',
        'location_unsupported': '📍 Location not supported by your browser.',
        'searching_doctors': '🔍 Searching for nearby doctors...',
        'doctors_found': '🏥 Found {count} nearby doctors/hospitals with 4+ star ratings.',
        'no_doctors': '❌ No nearby doctors found. Try expanding your search radius.',
        'error_analysis': 'Error analyzing symptoms. Please try again.',
        'error_doctors': '❌ Error finding doctors. Please try again.',
        'enable_location': '📍 Please enable location access to find nearby doctors.',
    },
    'ta': {
        'greeting': 'வணக்கம்! நான் உங்கள் மருத்துவ நோய் கண்டறிதல் உதவியாளர். இன்று நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?',
        'symptom_prompt': 'உங்கள் அறிகுறிகளை விவரிக்கவும்',
        'analyzing': 'உங்கள் அறிகுறிகளை பகுப்பாய்வு செய்கிறது...',
        'emergency': '🚨 அவசரம்: உடனடியாக 108 அழைக்கவும் அல்லது அவசர சிகிச்சைக்கு செல்லவும்!',
        'location_denied': '📍 இருப்பிட அணுகல் மறுக்கப்பட்டது. மருத்துவர் பரிந்துரைகள் குறைவாக இருக்கும்.',
        'location_unsupported': '📍 உங்கள் உலாவியில் இருப்பிடம் ஆதரிக்கப்படவில்லை.',
        'searching_doctors': '🔍 அருகிலுள்ள மருத்துவர்களைத் தேடுகிறது...',
        'doctors_found': '🏥 4+ நட்சத்திர மதிப்பீடுகளுடன் {count} அருகிலுள்ள மருத்துவர்கள்/மருத்துவமனைகள் கண்டறியப்பட்டன.',
        'no_doctors': '❌ அருகிலுள்ள மருத்துவர்கள் கிடைக்கவில்லை. தேடல் ஆரத்தை விரிவுபடுத்த முயற்சிக்கவும்.',
        'error_analysis': 'அறிகுறிகளை பகுப்பாய்வு செய்வதில் பிழை. மீண்டும் முயற்சிக்கவும்.',
        'error_doctors': '❌ மருத்துவர்களைக் கண்டறிவதில் பிழை. மீண்டும் முயற்சிக்கவும்.',
        'enable_location': '📍 அருகிலுள்ள மருத்துவர்களைக் கண்டறிய இருப்பிட அணுகலை இயக்கவும்.',
    },
    'tanglish': {
        'greeting': 'Vanakkam! Naan ungal medical diagnosis assistant. Innaiku naan ungalukku eppadi help panna mudiyum?',
        'symptom_prompt': 'Ungal symptoms ah describe pannunga',
        'analyzing': 'Ungal symptoms ah analyze pannitu irukku...',
        'emergency': '🚨 EMERGENCY: Udane 108 call pannunga illa ER ku ponga!',
        'location_denied': '📍 Location access deny pannitanga. Doctor recommendations limited ah irukum.',
        'location_unsupported': '📍 Ungal browser la location support illa.',
        'searching_doctors': '🔍 Nearby doctors ah search pannitu irukku...',
        'doctors_found': '🏥 4+ star ratings oda {count} nearby doctors/hospitals kandupidicha.',
        'no_doctors': '❌ Nearby doctors kidaikala. Search radius ah expand panna try pannunga.',
        'error_analysis': 'Symptoms analyze panna error. Marupadi try pannunga.',
        'error_doctors': '❌ Doctors kandupidikka error. Marupadi try pannunga.',
        'enable_location': '📍 Nearby doctors kandupidikka location access enable pannunga.',
    }
}

# Common medical terms mapping
MEDICAL_TERMS = {
    'en_to_ta': {
        'fever': 'காய்ச்சல்',
        'headache': 'தலைவலி',
        'cough': 'இருமல்',
        'cold': 'சளி',
        'pain': 'வலி',
        'stomach': 'வயிறு',
        'chest': 'மார்பு',
        'throat': 'தொண்டை',
        'body': 'உடல்',
        'breathing': 'சுவாசம்',
        'difficulty': 'சிரமம்',
        'nausea': 'குமட்டல்',
        'vomiting': 'வாந்தி',
        'diarrhea': 'வயிற்றுப்போக்கு',
        'fatigue': 'சோர்வு',
        'weakness': 'பலவீனம்',
        'dizziness': 'தலைச்சுற்றல்',
    },
    'en_to_tanglish': {
        'fever': 'kaichal',
        'headache': 'thalai vali',
        'cough': 'erumal',
        'cold': 'sali',
        'pain': 'vali',
        'stomach': 'vayiru',
        'chest': 'marbu',
        'throat': 'thondai',
        'body': 'udal',
        'breathing': 'suvasam',
        'difficulty': 'kastam',
        'nausea': 'kumattal',
        'vomiting': 'vanthi',
        'diarrhea': 'vayitru pokku',
        'fatigue': 'sorvu',
        'weakness': 'balaveenama',
        'dizziness': 'thalai sutral',
    }
}

def detect_language(text):
    """Detect if text is English, Tamil, or Tanglish"""
    if not text:
        return 'en'
    
    # Check for Tamil Unicode characters
    tamil_chars = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
    total_chars = len([c for c in text if c.isalpha()])
    
    if total_chars == 0:
        return 'en'
    
    tamil_ratio = tamil_chars / total_chars
    
    if tamil_ratio > 0.3:
        return 'ta'
    
    # Check for Tanglish patterns (Tamil words in English letters)
    tanglish_keywords = ['kaichal', 'vali', 'erumal', 'sali', 'vayiru', 'thalai', 'enakku', 'irukku', 'illa', 'eppadi', 'naan', 'ungal']
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in tanglish_keywords):
        return 'tanglish'
    
    return 'en'

def translate_text(text, target_lang='en'):
    """Get translated text for a key"""
    if target_lang in TRANSLATIONS and text in TRANSLATIONS[target_lang]:
        return TRANSLATIONS[target_lang][text]
    return TRANSLATIONS['en'].get(text, text)

def translate_message(message, source_lang, target_lang):
    """Translate medical terms in message"""
    if source_lang == target_lang:
        return message
    
    translated = message
    if source_lang == 'en' and target_lang == 'ta':
        for en_term, ta_term in MEDICAL_TERMS['en_to_ta'].items():
            translated = translated.replace(en_term, ta_term)
    elif source_lang == 'en' and target_lang == 'tanglish':
        for en_term, tanglish_term in MEDICAL_TERMS['en_to_tanglish'].items():
            translated = translated.replace(en_term, tanglish_term)
    
    return translated
