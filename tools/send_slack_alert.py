import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
BRIEFING_PATH = ".tmp/executive_briefing.md"

def send_to_slack():
    """
    Reads the generated executive briefing markdown and sends it to Slack via a Webhook.
    """
    if not SLACK_WEBHOOK_URL or SLACK_WEBHOOK_URL == "your_slack_webhook_here":
        print("Warning: SLACK_WEBHOOK_URL is not configured. Skipping Slack notification.")
        return

    if not os.path.exists(BRIEFING_PATH):
        print(f"Error: Briefing file not found at {BRIEFING_PATH}. Run the agent pipeline first.")
        sys.exit(1)

    with open(BRIEFING_PATH, "r", encoding="utf-8") as f:
        briefing_text = f.read()

    # Format payload for Slack
    payload = {
        "text": "📊 *Weekly GTM Revenue Intelligence Briefing*",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Weekly GTM Revenue Intelligence Briefing"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": briefing_text[:3000]  # Slack limit is 3,000 characters per block
                }
            }
        ]
    }

    print("Posting briefing to Slack...")
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"Slack post failed: {response.status_code} - {response.text}")
            sys.exit(1)
        print("Successfully posted briefing to Slack!")
    except Exception as e:
        print(f"Error communicating with Slack API: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    send_to_slack()
