from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from translations import detect_language, translate_text, TRANSLATIONS
from severity_analysis_enhanced import analyze_severity_indicators_detailed
import hashlib
import secrets

load_dotenv()

app = Flask(__name__)
CORS(app)

SEARCH_API_KEY = os.getenv('SEARCH_API_KEY')
SEARCH_API_URL = 'https://www.searchapi.io/api/v1/search'
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'

class DataCollector:
    def __init__(self, file='collected_data.json'):
        self.file = file
    
    def save(self, message, category, response, feedback=None):
        try:
            with open(self.file, 'r') as f:
                data = json.load(f)
        except:
            data = []
        data.append({'timestamp': datetime.now().isoformat(), 'message': message, 'category': category, 'response': response, 'feedback': feedback})
        with open(self.file, 'w') as f:
            json.dump(data, f, indent=2)

class TriageSystem:
    def __init__(self, config_file='triage_config.json'):
        self.config_file = config_file
        self.reload()
    
    def reload(self):
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        self.simple_kw = config['simple_keywords']
        self.complex_kw = config['complex_keywords']
        self.emergency_kw = config['emergency_keywords']
        self.simple_resp = config['simple_responses']
    
    def update_config(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        self.reload()
    
    def classify(self, message):
        msg = message.lower()
        if any(kw in msg for kw in self.emergency_kw):
            return 'emergency'
        if any(kw in msg for kw in self.complex_kw):
            return 'complex'
        if any(kw in msg for kw in self.simple_kw):
            return 'simple'
        return 'general'
    
    def get_simple_response(self, message):
        msg = message.lower()
        for key, resp in self.simple_resp.items():
            if key in msg:
                return resp
        return None

class MedicalDiagnosisModel:
    def __init__(self, data_file='data.json'):
        with open(data_file, 'r') as f:
            data = json.load(f)
        self.symptoms = data['symptoms']
        self.diseases = data['diseases']
        self.model = None
        self.scaler = StandardScaler()
        self.train_model()
    
    def train_model(self):
        np.random.seed(42)
        X = np.random.rand(500, len(self.symptoms))
        y = np.random.randint(0, len(self.diseases), 500)
        X_scaled = self.scaler.fit_transform(X)
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y)
    
    def predict(self, symptoms_dict):
        features = [symptoms_dict.get(symptom, 0) for symptom in self.symptoms]
        features_scaled = self.scaler.transform([features])
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        
        return {
            'diagnosis': self.diseases[prediction],
            'confidence': float(probabilities[prediction]),
            'all_probabilities': {
                disease: float(prob) 
                for disease, prob in zip(self.diseases, probabilities)
            }
        }

diagnosis_model = MedicalDiagnosisModel()
triage = TriageSystem()
collector = DataCollector()

# Simple user storage (use database in production)
users_db = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    name = data.get('name', '')
    
    if not email or not password or not name:
        return jsonify({'error': 'All fields are required'}), 400
    
    if email in users_db:
        return jsonify({'error': 'Email already exists'}), 400
    
    users_db[email] = {
        'email': email,
        'password': hash_password(password),
        'name': name,
        'created_at': datetime.now().isoformat()
    }
    
    token = secrets.token_urlsafe(32)
    
    return jsonify({
        'user': {'email': email, 'name': name},
        'token': token
    })

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = users_db.get(email)
    if not user or user['password'] != hash_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    token = secrets.token_urlsafe(32)
    
    return jsonify({
        'user': {'email': user['email'], 'name': user['name']},
        'token': token
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '').strip()
    user_lang = data.get('language', 'en')
    
    # Auto-detect language if not provided
    if not user_lang or user_lang == 'auto':
        user_lang = detect_language(message)
    
    # Use AI to decide if symptom cards needed
    try:
        headers = {'Authorization': f'Bearer {GROQ_API_KEY}', 'Content-Type': 'application/json'}
        prompt = f"User: '{message}'. Is this person reporting THEIR OWN health symptoms/problems (like 'I have fever', 'I feel sick', 'enakku kaichal irukku')? Reply ONLY 'YES' or 'NO'. Questions about medicine info are 'NO'."
        payload = {
            'model': 'llama-3.3-70b-versatile',
            'messages': [{'role': 'user', 'content': prompt}]
        }
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=5)
        if response.status_code == 200:
            ai_data = response.json()
            decision = ai_data.get('choices', [{}])[0].get('message', {}).get('content', '').strip().upper()
            if 'YES' in decision:
                return jsonify({'response': '', 'trigger_cards': True, 'language': user_lang})
    except:
        pass
    
    # Regular chat
    category = triage.classify(message)
    response_text = ''
    
    if category == 'emergency':
        response_text = translate_text('emergency', user_lang)
    elif category == 'simple':
        simple_resp = triage.get_simple_response(message)
        if simple_resp:
            response_text = simple_resp
    
    if not response_text:
        try:
            headers = {'Authorization': f'Bearer {GROQ_API_KEY}', 'Content-Type': 'application/json'}
            
            # Build system message with language instruction
            lang_instruction = ''
            if user_lang == 'ta':
                lang_instruction = ' Respond in Tamil language.'
            elif user_lang == 'tanglish':
                lang_instruction = ' Respond in Tanglish (Tamil written in English letters).'
            
            system_msg = """You are a smart AI Medical Voice Assistant similar to ChatGPT.

Your capabilities:

1. Language Support:
- Understand and respond in English, Tamil, and Tanglish.
- Always reply in the same language style as the user.

2. Voice Assistant Behavior:
- Keep responses short, natural, and human-like (2-3 sentences max).
- Speak like a real assistant (friendly and conversational).
- Avoid long paragraphs unless user asks.

3. Smart Conversation:
- If user gives symptoms → ask follow-up questions step by step.
- Example:
  User: "I have fever"
  You: "How many days have you had fever? Did you check temperature?"

4. Medical Logic:
- Classify symptoms as mild / moderate / severe.
- Suggest basic precautions (rest, hydration, etc.)
- If needed → recommend doctor consultation.

5. Safety Rules:
- Never give final diagnosis.
- For serious symptoms → say:
  "This might be serious. Please consult a doctor immediately."

6. Tone:
- Friendly
- Calm
- Supportive
- Not robotic

7. Tanglish Examples:
User: "Enaku headache iruku"
You: "Eppo irundhu headache iruku? Mild ah illa severe ah?"

8. English Example:
User: "I feel cold"
You: "Do you also have fever or body pain?"

Always behave like a real-time voice assistant, not like a static chatbot."""
            
            if category == 'complex':
                system_msg += ' For complex cases, recommend seeing a doctor.'
            
            system_msg += lang_instruction
            
            payload = {
                'model': 'llama-3.3-70b-versatile',
                'messages': [{'role': 'system', 'content': system_msg}, {'role': 'user', 'content': message}],
                'temperature': 0.7,
                'max_tokens': 150
            }
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                ai_data = response.json()
                response_text = ai_data.get('choices', [{}])[0].get('message', {}).get('content', '')
        except Exception as e:
            print(f'Error: {e}')
    
    if not response_text:
        response_text = 'No answer found.'
    
    collector.save(message, category, response_text)
    return jsonify({'response': response_text, 'type': category, 'triage': category, 'trigger_cards': False, 'language': user_lang})

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    data = request.json
    symptoms = data.get('symptoms', {})
    
    if not symptoms:
        return jsonify({'error': 'No symptoms provided'}), 400
    
    result = diagnosis_model.predict(symptoms)
    
    # Use Groq API to generate explanation
    try:
        headers = {'Authorization': f'Bearer {GROQ_API_KEY}', 'Content-Type': 'application/json'}
        prompt = f"Explain in 2-3 sentences: Patient has {result['diagnosis']} with {result['confidence']*100:.1f}% confidence based on their symptoms."
        payload = {
            'model': 'llama-3.3-70b-versatile',
            'messages': [{'role': 'user', 'content': prompt}]
        }
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            ai_data = response.json()
            explanation = ai_data.get('choices', [{}])[0].get('message', {}).get('content', '')
        else:
            explanation = ''
    except:
        explanation = ''
    
    return jsonify({
        'diagnosis': result['diagnosis'],
        'confidence': result['confidence'],
        'probabilities': result['all_probabilities'],
        'explanation': explanation
    })

@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    return jsonify({'symptoms': diagnosis_model.symptoms})

@app.route('/api/feedback', methods=['POST'])
def feedback():
    data = request.json
    message = data.get('message')
    rating = data.get('rating')
    try:
        with open('collected_data.json', 'r') as f:
            records = json.load(f)
        for r in reversed(records):
            if r['message'] == message:
                r['feedback'] = rating
                break
        with open('collected_data.json', 'w') as f:
            json.dump(records, f, indent=2)
        return jsonify({'status': 'ok'})
    except:
        return jsonify({'status': 'error'}), 500

@app.route('/api/analytics', methods=['GET'])
def analytics():
    try:
        with open('collected_data.json', 'r') as f:
            data = json.load(f)
        stats = {'total': len(data), 'simple': 0, 'complex': 0, 'emergency': 0, 'general': 0}
        for d in data:
            stats[d['category']] = stats.get(d['category'], 0) + 1
        return jsonify(stats)
    except:
        return jsonify({'total': 0})

@app.route('/api/triage/config', methods=['GET'])
def get_triage_config():
    with open('triage_config.json', 'r') as f:
        return jsonify(json.load(f))

@app.route('/api/triage/config', methods=['PUT'])
def update_triage_config():
    config = request.json
    triage.update_config(config)
    return jsonify({'status': 'ok'})

@app.route('/api/triage/keywords', methods=['POST'])
def add_keywords():
    data = request.json
    category = data.get('category')
    keywords = data.get('keywords', [])
    with open('triage_config.json', 'r') as f:
        config = json.load(f)
    key_map = {'simple': 'simple_keywords', 'complex': 'complex_keywords', 'emergency': 'emergency_keywords'}
    if category in key_map:
        config[key_map[category]].extend(keywords)
        triage.update_config(config)
        return jsonify({'status': 'ok'})
    return jsonify({'error': 'Invalid category'}), 400

@app.route('/api/triage/response', methods=['POST'])
def add_simple_response():
    data = request.json
    keyword = data.get('keyword')
    response = data.get('response')
    with open('triage_config.json', 'r') as f:
        config = json.load(f)
    config['simple_responses'][keyword] = response
    triage.update_config(config)
    return jsonify({'status': 'ok'})

@app.route('/api/collected-data', methods=['GET'])
def get_collected_data():
    try:
        with open('collected_data.json', 'r') as f:
            return jsonify(json.load(f))
    except:
        return jsonify([])

@app.route('/api/symptom-flow', methods=['GET'])
def get_symptom_flow():
    message = request.args.get('message', '')
    if message:
        try:
            headers = {'Authorization': f'Bearer {GROQ_API_KEY}', 'Content-Type': 'application/json'}
            prompt = f"User: '{message}'. Generate 5-7 medical triage questions as JSON. Format: {{\"flow\": [{{\"id\": \"fever\", \"question\": \"Do you have fever?\", \"type\": \"yesno\"}}, {{\"id\": \"duration\", \"question\": \"How long?\", \"type\": \"choice\", \"options\": [\"<24h\", \"1-3d\", \">7d\"]}}]}}. Types: yesno, choice, multichoice. Return ONLY valid JSON, no markdown."
            payload = {
                'model': 'llama-3.3-70b-versatile',
                'messages': [{'role': 'system', 'content': 'Return only valid JSON, no markdown or explanation.'}, {'role': 'user', 'content': prompt}]
            }
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                ai_data = response.json()
                content = ai_data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                if content.startswith('```'):
                    content = content.split('\n', 1)[1].rsplit('\n```', 1)[0]
                flow_data = json.loads(content)
                return jsonify(flow_data)
        except Exception as e:
            print(f'AI Flow Error: {e}')
    with open('symptom_flow.json', 'r') as f:
        return jsonify(json.load(f))

def analyze_severity_indicators(symptoms_data):
    indicators = {
        "fever_level": "none",
        "fever_severity": "none",
        "duration_concern": "low",
        "symptom_count": 0,
        "red_flags": []
    }
    
    if 'fever' in symptoms_data and symptoms_data['fever'] == 'yes':
        fever_temp = symptoms_data.get('fever_followup', '')
        if 'Below 100' in fever_temp:
            indicators['fever_level'] = 'low'
            indicators['fever_severity'] = 'MILD'
        elif '100-102' in fever_temp:
            indicators['fever_level'] = 'moderate'
            indicators['fever_severity'] = 'MODERATE'
        elif 'Above 102' in fever_temp:
            indicators['fever_level'] = 'high'
            indicators['fever_severity'] = 'SEVERE'
            indicators['red_flags'].append('High fever >102°F')
    
    duration = symptoms_data.get('duration', '')
    if 'More than a week' in duration:
        indicators['duration_concern'] = 'high'
        indicators['red_flags'].append('Prolonged symptoms')
    
    other_symptoms = symptoms_data.get('other_symptoms', [])
    if isinstance(other_symptoms, list):
        indicators['symptom_count'] = len([s for s in other_symptoms if s != 'None'])
    
    respiratory = symptoms_data.get('respiratory', [])
    if isinstance(respiratory, list) and 'Difficulty breathing' in respiratory:
        indicators['red_flags'].append('Difficulty breathing')
    
    if symptoms_data.get('pain') == 'yes':
        pain_locations = symptoms_data.get('pain_followup', [])
        if isinstance(pain_locations, list) and 'Chest' in pain_locations:
            indicators['red_flags'].append('Chest pain')
    
    return indicators

@app.route('/api/symptom-collect', methods=['POST'])
def collect_symptoms():
    data = request.json
    answers = data.get('answers', {})
    user_lang = data.get('language', 'en')
    
    if not answers:
        return jsonify({'error': 'No symptoms provided'}), 400
    
    severity_indicators = analyze_severity_indicators(answers)
    
    try:
        headers = {'Authorization': f'Bearer {GROQ_API_KEY}', 'Content-Type': 'application/json'}
        
        lang_instruction = ''
        if user_lang == 'ta':
            lang_instruction = ' Provide all text responses in Tamil language.'
        elif user_lang == 'tanglish':
            lang_instruction = ' Provide all text responses in Tanglish (Tamil written in English letters). Use words like: enakku, irukku, panna, eppadi, romba, konjam, doctor kitta ponga, hospital ku ponga.'
        
        prompt = f"""Analyze patient symptoms:
{json.dumps(answers, indent=2)}

Severity Indicators:
{json.dumps(severity_indicators, indent=2)}

Provide comprehensive medical analysis:
1. Severity: MILD/MODERATE/SEVERE (based on temperature, duration, red flags)
2. Urgency: low/medium/high/emergency
3. Top 3 possible conditions with probability percentages
4. Immediate actions to take
5. Home care recommendations
6. Warning signs to watch for
7. Medical specialty needed
8. Brief summary points
9. Overall assessment
10. Clear recommendation

{lang_instruction}

Return ONLY valid JSON in this exact format:
{{
  "severity": "MILD/MODERATE/SEVERE",
  "severity_score": 1-10,
  "severity_reasoning": "detailed explanation",
  "urgency": "low/medium/high/emergency",
  "conditions": [
    {{"name": "condition name", "probability": "percentage", "reasoning": "why this condition"}}
  ],
  "actions": ["action 1", "action 2"],
  "home_care": ["care 1", "care 2"],
  "warning_signs": ["sign 1", "sign 2"],
  "specialty": "medical specialty",
  "summary": ["point 1", "point 2"],
  "assessment": "overall assessment text",
  "recommendation": "clear recommendation"
}}"""
        
        payload = {
            'model': 'llama-3.3-70b-versatile',
            'messages': [
                {'role': 'system', 'content': 'You are an expert medical diagnostic AI. Provide detailed, accurate analysis. Return ONLY valid JSON, no markdown, no explanation.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.2,
            'max_tokens': 2000
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=20)
        
        if response.status_code != 200:
            print(f'Groq API error: {response.status_code} - {response.text}')
            raise Exception('AI service unavailable')
        
        ai_data = response.json()
        content = ai_data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        
        # Clean markdown formatting
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        result = json.loads(content)
        result['severity_indicators'] = severity_indicators
        result['language'] = user_lang
        
        # Ensure all required fields exist
        if 'severity' not in result:
            result['severity'] = 'MODERATE'
        if 'urgency' not in result:
            result['urgency'] = 'medium'
        if 'summary' not in result:
            result['summary'] = ['Symptoms analyzed']
        if 'assessment' not in result:
            result['assessment'] = 'Please consult a healthcare professional for proper diagnosis.'
        if 'recommendation' not in result:
            result['recommendation'] = 'Seek medical attention if symptoms persist or worsen.'
        
        collector.save(str(answers), 'symptom_collection', str(result))
        return jsonify(result)
        
    except json.JSONDecodeError as e:
        print(f'JSON parse error: {e}')
        print(f'Content: {content}')
        return jsonify({
            'severity': 'MODERATE',
            'severity_score': 5,
            'urgency': 'medium',
            'summary': ['Unable to fully analyze symptoms'],
            'assessment': 'Based on your symptoms, we recommend consulting a healthcare professional.',
            'recommendation': 'Please see a doctor for proper evaluation.',
            'severity_indicators': severity_indicators,
            'language': user_lang,
            'error': 'Analysis incomplete'
        })
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'severity': 'MODERATE',
            'severity_score': 5,
            'urgency': 'medium',
            'summary': ['Error occurred during analysis'],
            'assessment': 'We encountered an issue analyzing your symptoms.',
            'recommendation': 'Please consult a healthcare professional.',
            'severity_indicators': severity_indicators,
            'language': user_lang,
            'error': str(e)
        })

@app.route('/api/symptom-analyze', methods=['POST'])
def symptom_analyze():
    data = request.json
    answers = data.get('answers', {})
    location = data.get('location', {})
    user_lang = data.get('language', 'en')
    
    print(f'\n=== SYMPTOM ANALYSIS START ===')
    print(f'Answers: {json.dumps(answers, indent=2)}')
    print(f'Language: {user_lang}')
    
    if not answers:
        print('ERROR: No answers provided')
        return jsonify({
            'severity': 'MODERATE',
            'severity_score': 5,
            'urgency': 'medium',
            'summary': ['No symptoms provided'],
            'assessment': 'Please provide your symptoms for analysis.',
            'recommendation': 'Describe your symptoms in the chat.',
            'conditions': [],
            'actions': ['Describe your symptoms'],
            'home_care': ['Rest'],
            'warning_signs': ['Seek help if needed'],
            'specialty': 'General Physician',
            'language': user_lang
        })
    
    severity_indicators = analyze_severity_indicators_detailed(answers)
    print(f'Severity Score: {severity_indicators.get("severity_score")}/30')
    print(f'Problems Identified: {len(severity_indicators.get("problems_identified", []))}')
    print(f'Red Flags: {severity_indicators.get("red_flags")}')
    
    # Try AI analysis with fallback
    try:
        if not GROQ_API_KEY or GROQ_API_KEY == 'your_groq_api_key_here':
            raise Exception('GROQ_API_KEY not configured')
        
        headers = {'Authorization': f'Bearer {GROQ_API_KEY}', 'Content-Type': 'application/json'}
        
        lang_instruction = ''
        if user_lang == 'ta':
            lang_instruction = ' Respond in Tamil.'
        elif user_lang == 'tanglish':
            lang_instruction = ' Respond in Tanglish.'
        
        prompt = f"""Analyze these symptoms and provide DETAILED medical assessment:

Symptoms: {json.dumps(answers)}

DETAILED ANALYSIS:
{json.dumps(severity_indicators, indent=2)}

PROBLEMS IDENTIFIED:
{chr(10).join(severity_indicators.get('problems_identified', []))}

CLINICAL FINDINGS:
{chr(10).join(severity_indicators.get('clinical_findings', []))}

{lang_instruction}

Provide comprehensive JSON response with:
- severity (MILD/MODERATE/SEVERE/CRITICAL)
- urgency (low/medium/high/emergency)
- problems_list (list all identified problems clearly)
- conditions (list of 3-5 possible diagnoses with probability and detailed reasoning)
- actions (immediate steps with specific instructions)
- home_care (detailed self-care plan)
- warning_signs (specific signs requiring emergency care)
- specialty (which doctor to see)
- assessment (comprehensive evaluation explaining all problems)
- recommendation (clear next steps)

Return ONLY valid JSON, no markdown."""
        
        payload = {
            'model': 'llama-3.3-70b-versatile',
            'messages': [
                {'role': 'system', 'content': 'You are a medical AI. Return only valid JSON with complete medical assessment.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.3,
            'max_tokens': 2000
        }
        
        print('Calling Groq API...')
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        print(f'Groq Status: {response.status_code}')
        
        if response.status_code == 200:
            ai_data = response.json()
            content = ai_data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            print(f'Groq Response Length: {len(content)} chars')
            
            # Clean markdown
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            try:
                result = json.loads(content)
                print('AI Analysis: SUCCESS')
            except json.JSONDecodeError as je:
                print(f'JSON Parse Error: {je}')
                print(f'Content: {content[:500]}')
                raise Exception('Invalid JSON from AI')
            
            # Add detailed metadata
            result['severity_indicators'] = severity_indicators
            result['problems_identified'] = severity_indicators.get('problems_identified', [])
            result['clinical_findings'] = severity_indicators.get('clinical_findings', [])
            result['detailed_analysis'] = severity_indicators.get('detailed_analysis', {})
            result['language'] = user_lang
            result['severity_score'] = severity_indicators.get('severity_score', 5)
            
            # Ensure required fields
            if 'severity' not in result:
                result['severity'] = severity_indicators.get('overall_severity', 'MODERATE')
            if 'urgency' not in result:
                result['urgency'] = 'medium'
            if 'conditions' not in result:
                result['conditions'] = []
            if 'actions' not in result:
                result['actions'] = ['Monitor symptoms', 'Stay hydrated', 'Rest']
            if 'home_care' not in result:
                result['home_care'] = ['Rest', 'Drink fluids', 'Monitor temperature']
            if 'warning_signs' not in result:
                result['warning_signs'] = ['High fever', 'Difficulty breathing', 'Severe pain']
            if 'specialty' not in result:
                result['specialty'] = 'General Physician'
            if 'summary' not in result:
                result['summary'] = [f'Severity: {result["severity"]}', f'Urgency: {result["urgency"]}']
            if 'assessment' not in result:
                result['assessment'] = 'Based on your symptoms, medical evaluation is recommended.'
            if 'recommendation' not in result:
                result['recommendation'] = 'Consult a healthcare professional if symptoms persist.'
            
            # Find doctors if needed
            if result.get('urgency') in ['medium', 'high', 'emergency'] and location.get('lat'):
                print('Searching for nearby doctors...')
                doctors = find_nearby_doctors(location['lat'], location['lng'], result.get('specialty', 'hospital'))
                result['doctors'] = doctors
                print(f'Found {len(doctors)} doctors')
            
            print('=== ANALYSIS COMPLETE ===')
            print(f'Final Severity: {result["severity"]}')
            print(f'Final Urgency: {result["urgency"]}')
            return jsonify(result)
        else:
            print(f'Groq API Error: {response.status_code} - {response.text}')
            raise Exception(f'Groq API returned {response.status_code}')
            
    except Exception as e:
        print(f'ERROR in AI analysis: {e}')
        import traceback
        traceback.print_exc()
        print('Using FALLBACK response')
    
    # FALLBACK RESPONSE
    print('=== USING FALLBACK RESPONSE ===')
    score = severity_indicators.get('severity_score', 5)
    overall_severity = severity_indicators.get('overall_severity', 'MODERATE')
    red_flags = severity_indicators.get('red_flags', [])
    
    # Determine urgency from severity level and red flags
    urgency_level = severity_indicators.get('urgency_level', 'MEDIUM')
    
    if urgency_level == 'EMERGENCY':
        urgency = 'emergency'
    elif urgency_level == 'HIGH':
        urgency = 'high'
    elif urgency_level == 'MEDIUM':
        urgency = 'medium'
    else:
        urgency = 'low'
    
    # Build conditions based on likely patterns
    likely_conditions = severity_indicators.get('likely_conditions', [])
    conditions = []
    
    if 'Influenza-like illness' in likely_conditions:
        conditions.append({
            'name': 'Influenza (Flu)',
            'probability': '65%',
            'reasoning': 'Fever with multiple systemic symptoms (body aches, chills, headache)'
        })
        conditions.append({
            'name': 'Viral Fever',
            'probability': '25%',
            'reasoning': 'Fever with general symptoms'
        })
    elif 'Upper respiratory tract infection' in likely_conditions:
        conditions.append({
            'name': 'Upper Respiratory Infection',
            'probability': '70%',
            'reasoning': 'Respiratory symptoms with fever'
        })
        conditions.append({
            'name': 'Common Cold',
            'probability': '20%',
            'reasoning': 'Mild respiratory symptoms'
        })
    elif 'Gastroenteritis' in likely_conditions:
        conditions.append({
            'name': 'Gastroenteritis',
            'probability': '75%',
            'reasoning': 'GI symptoms present (nausea, vomiting, diarrhea)'
        })
        conditions.append({
            'name': 'Food Poisoning',
            'probability': '15%',
            'reasoning': 'Acute GI symptoms'
        })
    elif 'Viral fever' in likely_conditions:
        conditions.append({
            'name': 'Viral Fever',
            'probability': '60%',
            'reasoning': 'Fever is the primary symptom'
        })
        conditions.append({
            'name': 'Bacterial Infection',
            'probability': '25%',
            'reasoning': 'Fever with prolonged duration'
        })
    else:
        conditions.append({
            'name': 'Common Cold',
            'probability': '50%',
            'reasoning': 'Based on reported symptoms'
        })
        conditions.append({
            'name': 'Viral Infection',
            'probability': '30%',
            'reasoning': 'General viral illness'
        })
    
    fallback_result = {
        'severity': overall_severity,
        'severity_score': score,
        'severity_reasoning': f'Calculated severity score: {score}/30 based on symptom analysis',
        'urgency': urgency,
        'urgency_reasoning': f'Urgency level determined by severity score and red flags',
        'problems_identified': severity_indicators.get('problems_identified', []),
        'clinical_findings': severity_indicators.get('clinical_findings', []),
        'detailed_analysis': severity_indicators.get('detailed_analysis', {}),
        'conditions': conditions,
        'actions': [
            '1. Monitor your temperature regularly',
            '2. Stay well hydrated - drink 2-3 liters of water daily',
            '3. Get adequate rest',
            '4. Take paracetamol 500mg if fever above 100°F'
        ],
        'home_care': [
            'Rest in a comfortable environment',
            'Drink plenty of fluids (water, ORS, soups)',
            'Eat light, nutritious meals',
            'Use cold compress for fever',
            'Maintain good hygiene'
        ],
        'warning_signs': red_flags if red_flags else [
            'Fever above 103°F (39.4°C)',
            'Difficulty breathing or chest pain',
            'Severe headache or confusion',
            'Persistent vomiting',
            'Symptoms worsening after 3 days'
        ],
        'specialty': 'General Physician / Internal Medicine',
        'consultation_urgency': 'within 24-48 hours' if urgency in ['medium', 'high'] else 'routine follow-up',
        'summary': [
            f'Severity Level: {overall_severity}',
            f'Severity Score: {score}/30',
            f'Urgency: {urgency.upper()}',
            f'Symptoms Reported: {len(answers)}'
        ],
        'assessment': f'Based on your symptoms, you have {overall_severity.lower()} severity condition with a score of {score}/30. {"Immediate medical attention is recommended." if urgency in ["high", "emergency"] else "Monitor your symptoms and seek medical care if they worsen."}',
        'recommendation': f'Consult a {"doctor immediately" if urgency in ["high", "emergency"] else "healthcare professional within 24-48 hours" if urgency == "medium" else "doctor if symptoms persist beyond 3 days"}.',
        'follow_up': 'Reassess symptoms in 24-48 hours',
        'expected_duration': '3-7 days with proper care',
        'prevention': [
            'Maintain good hand hygiene',
            'Get adequate rest and sleep',
            'Stay hydrated',
            'Eat balanced, nutritious meals'
        ],
        'complications_risk': 'low' if score < 10 else 'medium' if score < 20 else 'high',
        'self_care_sufficient': score < 10,
        'severity_indicators': severity_indicators,
        'language': user_lang
    }
    
    # Find doctors if needed
    if urgency in ['medium', 'high', 'emergency'] and location.get('lat'):
        print('Searching for nearby doctors (fallback)...')
        doctors = find_nearby_doctors(location['lat'], location['lng'], 'hospital')
        fallback_result['doctors'] = doctors
        print(f'Found {len(doctors)} doctors')
    
    print('=== FALLBACK COMPLETE ===')
    print(f'Severity: {overall_severity}, Score: {score}, Urgency: {urgency}')
    return jsonify(fallback_result)

@app.route('/api/find-doctors', methods=['POST'])
def find_doctors_endpoint():
    data = request.json
    location = data.get('location', {})
    specialty = data.get('specialty', 'hospital')
    
    if not location.get('lat') or not location.get('lng'):
        return jsonify({'error': 'Location required'}), 400
    
    doctors = find_nearby_doctors(location['lat'], location['lng'], specialty)
    return jsonify({'doctors': doctors})

def find_nearby_doctors(lat, lng, specialty='hospital', radius=5000):
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not GOOGLE_MAPS_API_KEY or GOOGLE_MAPS_API_KEY == 'your_google_maps_key_here':
        print('Google Maps API key not configured')
        return []
    
    try:
        url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
        params = {
            'location': f'{lat},{lng}',
            'radius': radius,
            'type': 'hospital',
            'keyword': specialty,
            'key': GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            results = response.json().get('results', [])
            doctors = []
            
            for place in results:
                rating = place.get('rating', 0)
                if rating >= 4.0:
                    location_data = place['geometry']['location']
                    distance = calculate_distance(lat, lng, location_data['lat'], location_data['lng'])
                    
                    doctors.append({
                        'name': place['name'],
                        'address': place.get('vicinity', 'N/A'),
                        'rating': rating,
                        'total_ratings': place.get('user_ratings_total', 0),
                        'distance': f'{distance} km',
                        'phone': 'N/A',
                        'maps_url': f"https://www.google.com/maps/search/?api=1&query={location_data['lat']},{location_data['lng']}&query_place_id={place['place_id']}",
                        'booking_url': place.get('website', ''),
                        'open_now': place.get('opening_hours', {}).get('open_now', None)
                    })
            
            doctors.sort(key=lambda x: (x['rating'], -float(x['distance'].split()[0])), reverse=True)
            return doctors[:5]
    except Exception as e:
        print(f'Doctor search error: {e}')
    
    return []

def calculate_distance(lat1, lng1, lat2, lng2):
    from math import radians, sin, cos, sqrt, atan2
    R = 6371
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return round(R * c, 2)


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
