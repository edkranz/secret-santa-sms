from flask import Flask, render_template, request, jsonify
import json
import os
import secrets
import requests
import re
from typing import List, Optional
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import Participant, Couple, DrawResult
from draw_service import DrawService
from email_service import AzureEmailService
from config import Config

app = Flask(__name__)

API_KEY = os.environ.get('API_KEY')
TURNSTILE_SECRET_KEY = os.environ.get('TURNSTILE_SECRET_KEY')
TURNSTILE_SITE_KEY = os.environ.get('TURNSTILE_SITE_KEY')

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def validate_email(email: str) -> bool:
    """Validate email format using regex"""
    if not email:
        return False
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def verify_turnstile(token):
    """Verify Cloudflare Turnstile token"""
    if not TURNSTILE_SECRET_KEY:
        return True
    
    try:
        response = requests.post(
            'https://challenges.cloudflare.com/turnstile/v0/siteverify',
            data={
                'secret': TURNSTILE_SECRET_KEY,
                'response': token
            },
            timeout=5
        )
        result = response.json()
        return result.get('success', False)
    except Exception as e:
        app.logger.error(f"Turnstile verification failed: {e}")
        return False

def require_api_key(f):
    """
    Optional: For server-to-server API calls only
    Regular users don't need to provide this
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_key = request.headers.get('X-API-Key')
        
        # If API key is provided, validate it (for programmatic access)
        if provided_key:
            if not API_KEY:
                return jsonify({'error': 'Server configuration error'}), 500
            if not secrets.compare_digest(provided_key, API_KEY):
                return jsonify({'error': 'Invalid API key'}), 403
        
        # If no API key provided, that's fine - reCAPTCHA + rate limiting protect us
        return f(*args, **kwargs)
    return decorated_function

def require_turnstile(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not TURNSTILE_SECRET_KEY:
            return f(*args, **kwargs)
        
        turnstile_token = request.json.get('turnstile_token') if request.json else None
        
        if not turnstile_token:
            return jsonify({'error': 'Turnstile verification required'}), 400
        
        if not verify_turnstile(turnstile_token):
            return jsonify({'error': 'Turnstile verification failed. Please try again.'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def get_email_service():
    config = Config()
    config.validate_email()
    return AzureEmailService(
        connection_string=config.azure_connection_string,
        sender_email=config.azure_sender_email,
        template_path=config.email_template_path
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Return public configuration like Turnstile site key"""
    return jsonify({
        'turnstile_site_key': TURNSTILE_SITE_KEY,
        'turnstile_enabled': bool(TURNSTILE_SECRET_KEY)
    })

@app.route('/api/draw', methods=['POST'])
@limiter.limit("3 per hour")
@require_turnstile
@require_api_key
def perform_draw():
    try:
        data = request.json
        selected_participants = data.get('participants', [])
        exclusions = data.get('exclusions', [])
        custom_message = data.get('message', '')
        gift_limit = data.get('gift_limit', '$100')
        
        if len(selected_participants) < 2:
            return jsonify({'error': 'Need at least 2 participants'}), 400
        
        for p in selected_participants:
            email = p.get('email')
            if email and not validate_email(email):
                return jsonify({'error': f'Invalid email address for {p.get("name", "participant")}: {email}'}), 400
        
        email_set = set()
        for p in selected_participants:
            email = p.get('email')
            if email:
                email_lower = email.lower()
                if email_lower in email_set:
                    return jsonify({'error': f'Duplicate email address: {email}'}), 400
                email_set.add(email_lower)
        
        participants = [
            Participant(
                name=p['name'],
                email=p.get('email'),
                phone_number=p.get('phone_number')
            )
            for p in selected_participants
        ]
        
        participants_by_name = {p.name: p for p in participants}
        couples = []
        for exclusion in exclusions:
            name1 = exclusion.get('person1')
            name2 = exclusion.get('person2')
            if name1 in participants_by_name and name2 in participants_by_name:
                couples.append(Couple(
                    person1=participants_by_name[name1],
                    person2=participants_by_name[name2]
                ))
        
        draw_service = DrawService(participants, couples if couples else None)
        results = draw_service.draw()
        
        email_service = get_email_service()
        email_results = []
        
        for result in results:
            if not result.giver.email:
                email_results.append({
                    'giver': result.giver.name,
                    'receiver': result.receiver.name,
                    'status': 'skipped',
                    'reason': 'No email address'
                })
                continue
            
            success = email_service.send_notification(
                result.giver.email,
                result.giver.name,
                result.receiver.name,
                custom_message,
                gift_limit
            )
            
            email_results.append({
                'giver': result.giver.name,
                'receiver': result.receiver.name,
                'status': 'sent' if success else 'failed'
            })
        
        return jsonify({
            'success': True,
            'results': email_results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port, debug=False)

