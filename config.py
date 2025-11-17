import os
from dotenv import load_dotenv
from typing import Optional


class Config:
    def __init__(self, env_file: Optional[str] = None):
        load_dotenv(env_file)
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_from_number = os.getenv("TWILIO_FROM_NUMBER")
        self.twilio_from_name = os.getenv("TWILIO_FROM_NAME")
        
        self.azure_connection_string = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING")
        self.azure_sender_email = os.getenv("AZURE_SENDER_EMAIL")
        self.email_template_path = os.getenv("EMAIL_TEMPLATE_PATH")

    def validate_sms(self) -> None:
        missing = []
        if not self.twilio_account_sid:
            missing.append("TWILIO_ACCOUNT_SID")
        if not self.twilio_auth_token:
            missing.append("TWILIO_AUTH_TOKEN")
        if not self.twilio_from_number and not self.twilio_from_name:
            missing.append("TWILIO_FROM_NUMBER or TWILIO_FROM_NAME")
        
        if missing:
            raise ValueError(
                f"Missing required environment variables for SMS: {', '.join(missing)}\n"
                "Please set them before running the application."
            )

    def validate_email(self) -> None:
        missing = []
        if not self.azure_connection_string:
            missing.append("AZURE_COMMUNICATION_CONNECTION_STRING")
        if not self.azure_sender_email:
            missing.append("AZURE_SENDER_EMAIL")
        
        if missing:
            raise ValueError(
                f"Missing required environment variables for Email: {', '.join(missing)}\n"
                "Please set them before running the application."
            )

    def validate(self) -> None:
        self.validate_sms()

