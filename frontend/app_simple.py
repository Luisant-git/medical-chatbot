from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
import secrets
from database import Database

load_dotenv()

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'

db = Database()

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    name = data.get('name', '')
    
    if not email or not password or not name:
        return jsonify({'error': 'All fields are required'}), 400
    
    user = db.create_user(name, email, password)
    
    if not user:
        return jsonify({'error': 'Email already exists'}), 400
    
    token = secrets.token_urlsafe(32)
    
    return jsonify({
        'user': {'id': user['id'], 'email': user['email'], 'name': user['name']},
        'token': token
    })

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    # Hardcoded fallback credentials
    if email == 'vikyvinoth1@gmail.com' and password == 'vinoth123':
        return jsonify({
            'user': {'id': 'hardcoded_user', 'email': 'vikyvinoth1@gmail.com', 'name': 'Vinoth'},
            'token': 'token_hardcoded_user'
        })
    
    try:
        user = db.verify_user(email, password)
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        token = secrets.token_urlsafe(32)
        
        return jsonify({
            'user': {'id': user['id'], 'email': user['email'], 'name': user['name']},
            'token': token
        })
    except Exception as e:
        print(f'Login error: {e}')
        # Fallback to hardcoded on database error
        if email == 'vikyvinoth1@gmail.com' and password == 'vinoth123':
            return jsonify({
                'user': {'id': 'hardcoded_user', 'email': 'vikyvinoth1@gmail.com', 'name': 'Vinoth'},
                'token': 'token_hardcoded_user'
            })
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'response': 'Please enter a message'}), 400
    
    try:
        headers = {'Authorization': f'Bearer {GROQ_API_KEY}', 'Content-Type': 'application/json'}
        
        system_msg = """You are a smart AI Medical Assistant.

Your capabilities:
1. Understand medical symptoms and provide helpful guidance
2. Keep responses short and conversational (2-4 sentences)
3. Ask follow-up questions to understand symptoms better
4. Provide basic health advice and recommendations
5. Always recommend consulting a doctor for serious symptoms

Safety Rules:
- Never give final diagnosis
- For serious symptoms, recommend immediate medical attention
- Be friendly, calm, and supportive

Example:
User: "I have fever"
You: "How many days have you had the fever? Have you checked your temperature?"
"""
        
        payload = {
            'model': 'llama-3.3-70b-versatile',
            'messages': [
                {'role': 'system', 'content': system_msg},
                {'role': 'user', 'content': message}
            ],
            'temperature': 0.7,
            'max_tokens': 200
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            ai_data = response.json()
            response_text = ai_data.get('choices', [{}])[0].get('message', {}).get('content', '')
            return jsonify({'response': response_text})
        else:
            return jsonify({'response': 'AI service unavailable. Please try again.'}), 500
            
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'response': 'Error connecting to AI service. Please try again.'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
