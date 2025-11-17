from typing import List
from models import DrawResult
from notification_service import NotificationService


class TwilioSMSService(NotificationService):
    def __init__(self, account_sid: str, auth_token: str, from_number: str = None, from_name: str = None):
        try:
            from twilio.rest import Client
        except ImportError:
            raise ImportError("twilio package not installed. Run: pip install twilio")
        
        if not from_number and not from_name:
            raise ValueError("Either from_number or from_name must be provided")
        
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number
        self.from_name = from_name

    def send_notification(self, recipient: str, recipient_name: str, receiver_name: str) -> bool:
        try:
            message = self._format_message(recipient_name, receiver_name)
            from_sender = self.from_name if self.from_name else self.from_number
            self.client.messages.create(
                body=message,
                from_=from_sender,
                to=recipient
            )
            return True
        except Exception as e:
            print(f"Failed to send SMS to {recipient}: {e}")
            return False

    def send_draw_results(self, results: List[DrawResult]) -> None:
        for result in results:
            if not result.giver.phone_number:
                print(f"✗ Skipping {result.giver.name} - no phone number provided")
                continue
            
            success = self.send_notification(
                result.giver.phone_number,
                result.giver.name,
                result.receiver.name
            )
            if success:
                print(f"✓ Sent SMS to {result.giver.name}")
            else:
                print(f"✗ Failed to send SMS to {result.giver.name}")

    def _format_message(self, name: str, receiver_name: str) -> str:
        return f"🎅 Ho ho ho, {name}!\n\n🎁 You are buying a gift for:\n✨ {receiver_name} ✨\n\nKeep it secret! 🤫"

