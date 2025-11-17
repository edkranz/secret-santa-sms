import argparse
import json
import sys
from typing import List, Optional
from models import Participant, Couple, DrawResult
from draw_service import DrawService
from notification_service import NotificationService
from config import Config
from json_loader import load_participants_from_json


class SecretSantaApp:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def run(
        self,
        participants: List[Participant],
        couples: Optional[List[Couple]] = None
    ) -> List[DrawResult]:
        draw_service = DrawService(participants, couples)
        results = draw_service.draw()
        
        print(f"\n🎄 Secret Santa Draw Complete! 🎄")
        print(f"Drew {len(results)} pairs\n")
        
        self.notification_service.send_draw_results(results)
        
        return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Secret Santa Notification Draw")
    parser.add_argument(
        '--json',
        type=str,
        default='participants.json',
        help='Path to JSON file with participants and couples (default: participants.json)'
    )
    parser.add_argument(
        '--method',
        type=str,
        choices=['sms', 'email'],
        default='sms',
        help='Notification method: sms or email (default: sms)'
    )
    args = parser.parse_args()
    
    try:
        participants, couples = load_participants_from_json(args.json)
    except FileNotFoundError:
        print(f"Error: JSON file '{args.json}' not found.")
        print(f"Please create a JSON file or copy 'participants.json.example' to 'participants.json'")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in '{args.json}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading participants: {e}")
        sys.exit(1)
    
    config = Config()
    
    if args.method == 'sms':
        config.validate_sms()
        from sms_service import TwilioSMSService
        notification_service = TwilioSMSService(
            account_sid=config.twilio_account_sid,
            auth_token=config.twilio_auth_token,
            from_number=config.twilio_from_number,
            from_name=config.twilio_from_name
        )
    else:
        config.validate_email()
        from email_service import AzureEmailService
        notification_service = AzureEmailService(
            connection_string=config.azure_connection_string,
            sender_email=config.azure_sender_email,
            template_path=config.email_template_path
        )
    
    app = SecretSantaApp(notification_service)
    app.run(participants, couples)

