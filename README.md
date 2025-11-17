# Secret Santa Notifications

A Python application that performs a Secret Santa draw and sends notifications (SMS via Twilio or Email via Azure Communication Services) to each participant with their assigned recipient, without spoiling the surprise for the organiser!

## Features

- Secret Santa draw with automatic pairing
- Couples exclusion: Couples will never draw each other
- SMS notifications via Twilio API
- Email notifications via Azure Communication Services
- Customizable HTML email templates with `{recipient_name}` and `{receiver_name}` placeholders

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure credentials:
   - Copy `env.example` to `.env`: `cp env.example .env`
   - Edit `.env` and fill in your credentials:
   
   **For SMS (Twilio):**
   - Set `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`
   - Set `TWILIO_FROM_NAME=SANTA` to send SMS from "SANTA" (alphanumeric sender ID)
   - Or use `TWILIO_FROM_NUMBER` with a Twilio phone number
   
   **For Email (Azure Communication Services):**
   - Set `AZURE_COMMUNICATION_CONNECTION_STRING` (your Azure Communication Services connection string)
   - Set `AZURE_SENDER_EMAIL` (your verified sender email address)
   - Optionally set `EMAIL_TEMPLATE_PATH` to use a custom HTML template (default: `email_template.html`)

3. Create participants JSON file:
   - Copy `participants.json.example` to `participants.json`: `cp participants.json.example participants.json`
   - Edit `participants.json` with your participants and couples
   - Include `phone_number` for SMS or `email` for email notifications (or both)

## Usage

### Basic Usage

1. Edit `participants.json` with your participants:
```json
{
  "participants": [
    {
      "name": "Alice",
      "phone_number": "+1234567890",
      "email": "alice@example.com"
    },
    {
      "name": "Bob",
      "phone_number": "+1234567891",
      "email": "bob@example.com"
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

**Using SMS:**
```bash
python main.py --method sms
```

**Using Email:**
```bash
python main.py --method email
```

Or specify a custom JSON file:
```bash
python main.py --json my_participants.json --method email
```

### Email Templates

You can customize the email template by editing `email_template.html` (or setting `EMAIL_TEMPLATE_PATH` in your `.env` file). The template supports the following placeholders:

- `{recipient_name}` - The name of the person receiving the email
- `{receiver_name}` - The name of the person they need to buy a gift for

Example template usage:
```html
<h1>Hello {recipient_name}!</h1>
<p>You are buying a gift for: <strong>{receiver_name}</strong></p>
```

### Programmatic Usage

**Using SMS:**
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

**Using Email:**
```python
from main import SecretSantaApp
from models import Participant, Couple
from email_service import AzureEmailService

participants = [
    Participant(name="Alice", email="alice@example.com"),
    Participant(name="Bob", email="bob@example.com"),
]

couples = [Couple(person1=participants[0], person2=participants[1])]

email_service = AzureEmailService(
    connection_string="your_azure_connection_string",
    sender_email="santa@yourdomain.com",
    template_path="email_template.html"
)

app = SecretSantaApp(email_service)
results = app.run(participants, couples)
```

## Architecture

The project follows separation of concerns:

- **models.py**: Data models (Participant, Couple, DrawResult)
- **draw_service.py**: Secret Santa drawing logic
- **notification_service.py**: Notification service abstraction
- **sms_service.py**: SMS sending implementation (Twilio)
- **email_service.py**: Email sending implementation (Azure Communication Services)
- **template_loader.py**: HTML email template loader with placeholder replacement
- **config.py**: Configuration management
- **json_loader.py**: JSON file parsing for participants and couples
- **main.py**: Application orchestration

## How It Works

1. The `DrawService` validates participants and couples
2. It performs a random draw ensuring:
   - No one draws themselves
   - Couples don't draw each other
3. The `NotificationService` (SMS or Email) sends notifications to each participant with their assigned recipient
4. Each participant only receives their own assignment
5. For email, the template loader replaces `{recipient_name}` and `{receiver_name}` placeholders with actual names

## Notes

**SMS (Twilio):**
- Phone numbers must be in E.164 format (e.g., +1234567890)
- Use `TWILIO_FROM_NAME` (e.g., "SANTA") to send SMS with a custom sender name that appears in contacts
- Alphanumeric sender IDs may not be supported in all countries/regions
- Ensure your Twilio account has sufficient credits

**Email (Azure Communication Services):**
- You need to set up an Azure Communication Services resource and provision an email domain
- The sender email address must be verified in Azure Communication Services
- HTML templates support `{recipient_name}` and `{receiver_name}` placeholders
- If no template is specified, a default HTML template will be used

**General:**
- The draw algorithm will retry up to 1000 times if a valid draw cannot be found initially
- Participants can have both `phone_number` and `email` fields, but only the relevant one will be used based on the selected method

