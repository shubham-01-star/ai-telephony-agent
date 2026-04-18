# AI Telephony Agent

An AI-powered telephony agent built with [VideoSDK](https://videosdk.live/) and Google Gemini. Make and receive phone calls with a real-time AI voice assistant.

## Features

- 🤖 Real-time AI voice conversations via phone
- 📞 Outbound SIP calls via Twilio
- 🎙️ Powered by Google Gemini 2.5 Flash native audio
- 🌍 Multi-language support

## Requirements

- Python **3.11+** (Python 3.12 recommended)
- `videosdk-agents >= 1.0.8` (Required for `.Pipeline()` class and optimized native audio)
- [VideoSDK account](https://app.videosdk.live/) with API Key + Secret
- [Google AI Studio](https://aistudio.google.com/apikey) API Key
- [Twilio account](https://twilio.com/) with a phone number (for SIP calling)

## Setup

### 1. Clone & create virtual environment

```bash
git clone <your-repo-url>
cd Telephony-agent

# Use Python 3.12 (3.10 is too old for videosdk-agents)
python3.12 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### 4. Generate VideoSDK JWT Token

```bash
# For agent authentication (rtc role)
python generate_token.py

# For API calls like outbound SIP (crawler role)
python generate_token.py crawler
```

Copy the generated token into `.env` as `VIDEOSDK_AUTH_TOKEN`.

> ⚠️ Ensure your token has BOTH `rtc` and `crawler` roles. A purely `rtc` token will fail VideoSDK analytics telemetry under the hood and result in massive `401 Unauthorized` log spam, severely increasing your latency.

> ⚠️ Token expires every **24 hours** — regenerate as needed.

## Running the Agent

```bash
python main.py
```

The agent will register with VideoSDK and print a playground URL for testing.

## Making an Outbound Call

```bash
# Generate a crawler-role token first
CRAWLER_TOKEN=$(python generate_token.py crawler | grep -A1 '\-\-\-\-' | tail -1)

curl --request POST \
  --url https://api.videosdk.live/v2/sip/call \
  --header "Authorization: $CRAWLER_TOKEN" \
  --header 'Content-Type: application/json' \
  --data '{
    "gatewayId": "your_outbound_gateway_id",
    "sipCallTo": "+1234567890",
    "agentId": "MyTelephonyAgent"
  }'
```

## Telephony Setup (Twilio + VideoSDK)

See the full setup guide in [`telephony_setup_guide.md`](./telephony_setup_guide.md).

## Project Structure

```
├── main.py              # Core agent logic
├── generate_token.py    # JWT token generator
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
└── .env                 # Your actual credentials (never commit!)
```
