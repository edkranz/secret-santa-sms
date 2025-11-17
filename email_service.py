from typing import List, Optional
from models import DrawResult
from notification_service import NotificationService
from template_loader import TemplateLoader


class AzureEmailService(NotificationService):
    def __init__(
        self,
        connection_string: str,
        sender_email: str,
        template_path: Optional[str] = None
    ):
        try:
            from azure.communication.email import EmailClient
        except ImportError:
            raise ImportError("azure-communication-email package not installed. Run: pip install azure-communication-email")
        
        self.client = EmailClient.from_connection_string(connection_string)
        self.sender_email = sender_email
        self.template_loader = TemplateLoader(template_path) if template_path else None

    def send_notification(self, recipient: str, recipient_name: str, receiver_name: str, message: str = '', gift_limit: str = '$100') -> bool:
        try:
            if self.template_loader:
                html_content = self.template_loader.render(recipient_name, receiver_name, message, gift_limit)
                plain_text_content = self._generate_plain_text(recipient_name, receiver_name, message, gift_limit)
            else:
                html_content = self._generate_default_html(recipient_name, receiver_name, message, gift_limit)
                plain_text_content = self._generate_plain_text(recipient_name, receiver_name, message, gift_limit)

            email_message = {
                "senderAddress": self.sender_email,
                "recipients": {
                    "to": [{"address": recipient, "displayName": recipient_name}]
                },
                "content": {
                    "subject": f"🎅 Secret Santa Assignment for {recipient_name}!",
                    "html": html_content,
                    "plainText": plain_text_content
                }
            }

            poller = self.client.begin_send(email_message)
            poller.wait()
            return True
        except Exception as e:
            print(f"Failed to send email to {recipient}: {e}")
            return False

    def send_draw_results(self, results: List[DrawResult], message: str = '', gift_limit: str = '$100') -> None:
        for result in results:
            if not result.giver.email:
                print(f"✗ Skipping {result.giver.name} - no email address provided")
                continue
            
            success = self.send_notification(
                result.giver.email,
                result.giver.name,
                result.receiver.name,
                message,
                gift_limit
            )
            if success:
                print(f"✓ Sent email to {result.giver.name}")
            else:
                print(f"✗ Failed to send email to {result.giver.name}")

    def _generate_default_html(self, name: str, receiver_name: str, message: str = '', gift_limit: str = '$100') -> str:
        message_section = f'<div style="background-color: #fff9e6; border-left: 4px solid #ff9800; padding: 15px; margin: 20px 0; border-radius: 4px;"><p style="margin: 0; font-style: italic; color: #333;">{message}</p></div>' if message else ''
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h1 style="color: #d32f2f;">🎅 Ho ho ho, {name}!</h1>
            <p>🎁 You are buying a gift for:</p>
            <h2 style="color: #1976d2;">✨ {receiver_name} ✨</h2>
            {message_section}
            <p>The price limit is {gift_limit}. Happy gifting! 🎁</p>
            <p>Keep it secret! 🤫</p>
        </body>
        </html>
        """

    def _generate_plain_text(self, name: str, receiver_name: str, message: str = '', gift_limit: str = '$100') -> str:
        message_text = f'\n\n{message}\n' if message else '\n'
        return f"🎅 Ho ho ho, {name}!\n\n🎁 You are buying a gift for:\n✨ {receiver_name} ✨{message_text}The price limit is {gift_limit}. Happy gifting! 🎁\nKeep it secret! 🤫"

