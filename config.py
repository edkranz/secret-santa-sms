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

    def validate(self) -> None:
        missing = []
        if not self.twilio_account_sid:
            missing.append("TWILIO_ACCOUNT_SID")
        if not self.twilio_auth_token:
            missing.append("TWILIO_AUTH_TOKEN")
        if not self.twilio_from_number and not self.twilio_from_name:
            missing.append("TWILIO_FROM_NUMBER or TWILIO_FROM_NAME")
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                "Please set them before running the application."
            )

