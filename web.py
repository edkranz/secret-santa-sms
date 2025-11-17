from flask import Flask, render_template, request, jsonify
import json
import os
from typing import List, Optional
from models import Participant, Couple, DrawResult
from draw_service import DrawService
from email_service import AzureEmailService
from config import Config

app = Flask(__name__)

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

@app.route('/api/draw', methods=['POST'])
def perform_draw():
    try:
        data = request.json
        selected_participants = data.get('participants', [])
        exclusions = data.get('exclusions', [])
        custom_message = data.get('message', '')
        gift_limit = data.get('gift_limit', '$100')
        
        if len(selected_participants) < 2:
            return jsonify({'error': 'Need at least 2 participants'}), 400
        
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
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)

