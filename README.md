# Secret Santa SMS

A Python application that performs a Secret Santa draw and sends SMS notifications via Twilio to each participant with their assigned recipient, without spoiling the surprise for the organiser!

## Features

- Secret Santa draw with automatic pairing
- Couples exclusion: Couples will never draw each other
- SMS notifications via Twilio API

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Twilio credentials:
   - Copy `env.example` to `.env`: `cp env.example .env`
   - Edit `.env` and fill in your Twilio credentials
   - Set `TWILIO_FROM_NAME=SANTA` to send SMS from "SANTA" (alphanumeric sender ID)
   - Or use `TWILIO_FROM_NUMBER` with a Twilio phone number

3. Create participants JSON file:
   - Copy `participants.json.example` to `participants.json`: `cp participants.json.example participants.json`
   - Edit `participants.json` with your participants and couples

## Usage

### Basic Usage

1. Edit `participants.json` with your participants:
```json
{
  "participants": [
    {
      "name": "Alice",
      "phone_number": "+1234567890"
    },
    {
      "name": "Bob",
      "phone_number": "+1234567891"
    }
  ],
  "couples": [
    {
      "person1": "Alice",
      "person2": "Bob"
    }
  ]
}
```

2. Run the application:
```bash
python main.py
```

Or specify a custom JSON file:
```bash
python main.py --json my_participants.json
```

### Programmatic Usage

```python
from main import SecretSantaApp
from models import Participant, Couple
from sms_service import TwilioSMSService

participants = [
    Participant(name="Alice", phone_number="+1234567890"),
    Participant(name="Bob", phone_number="+1234567891"),
]

couples = [Couple(person1=participants[0], person2=participants[1])]

sms_service = TwilioSMSService(
    account_sid="your_sid",
    auth_token="your_token",
    from_number="+1234567890"
)

app = SecretSantaApp(sms_service)
results = app.run(participants, couples)
```

## Architecture

The project follows separation of concerns:

- **models.py**: Data models (Participant, Couple, DrawResult)
- **draw_service.py**: Secret Santa drawing logic
- **sms_service.py**: SMS sending abstraction (with Twilio implementation)
- **config.py**: Configuration management
- **json_loader.py**: JSON file parsing for participants and couples
- **main.py**: Application orchestration

## How It Works

1. The `DrawService` validates participants and couples
2. It performs a random draw ensuring:
   - No one draws themselves
   - Couples don't draw each other
3. The `SMSService` sends SMS messages to each participant with their assigned recipient
4. Each participant only receives their own assignment

## Notes

- Phone numbers must be in E.164 format (e.g., +1234567890)
- Use `TWILIO_FROM_NAME` (e.g., "SANTA") to send SMS with a custom sender name that appears in contacts
- Alphanumeric sender IDs may not be supported in all countries/regions
- Ensure your Twilio account has sufficient credits
- The draw algorithm will retry up to 1000 times if a valid draw cannot be found initially

