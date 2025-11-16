from abc import ABC, abstractmethod
from typing import List
from models import DrawResult


class SMSService(ABC):
    @abstractmethod
    def send_message(self, phone_number: str, message: str) -> bool:
        pass

    @abstractmethod
    def send_draw_results(self, results: List[DrawResult]) -> None:
        pass


class TwilioSMSService(SMSService):
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

    def send_message(self, phone_number: str, message: str) -> bool:
        try:
            from_sender = self.from_name if self.from_name else self.from_number
            self.client.messages.create(
                body=message,
                from_=from_sender,
                to=phone_number
            )
            return True
        except Exception as e:
            print(f"Failed to send SMS to {phone_number}: {e}")
            return False

    def send_draw_results(self, results: List[DrawResult]) -> None:
        for result in results:
            message = self._format_message(result.giver.name, result.receiver.name)
            success = self.send_message(result.giver.phone_number, message)
            if success:
                print(f"✓ Sent SMS to {result.giver.name}")
            else:
                print(f"✗ Failed to send SMS to {result.giver.name}")

    def _format_message(self, name: str, receiver_name: str) -> str:
        return f"🎅 Ho ho ho, {name}!\n\n🎁 You are buying a gift for:\n✨ {receiver_name} ✨\n\nKeep it secret! 🤫"

