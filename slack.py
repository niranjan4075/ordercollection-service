import os
import logging
import requests

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load the Slack Bot Token
slack_token = os.getenv("SLACK_BOT_TOKEN")

# Set the Slack API endpoint
url = "https://slack.com/api/chat.postMessage"

# Set the message parameters
payload = {
    "channel": "C0XXXXXX",  # Replace with your channel ID
    "text": "Please approve or reject the request:",  # Text fallback
    "blocks": [
        {
            "type": "section",
            "block_id": "section-1",
            "text": {
                "type": "mrkdwn",
                "text": "*Please approve or reject the request:*"
            },
            "accessory": {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Approve"
                        },
                        "action_id": "approve_button",
                        "style": "primary"  # Adds a primary button style
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Reject"
                        },
                        "action_id": "reject_button",
                        "style": "danger"  # Adds a danger button style
                    }
                ]
            }
        }
    ]
}

# Set the headers including the Authorization with the Bearer Token
headers = {
    "Authorization": f"Bearer {slack_token}",
    "Content-Type": "application/json"
}

# Make the POST request to send the message
response = requests.post(url, headers=headers, json=payload)

# Check if the message was successfully sent
if response.status_code == 200:
    data = response.json()
    if data.get("ok"):
        logging.info("Message sent successfully")
    else:
        logging.error(f"Error sending message: {data.get('error')}")
else:
    logging.error(f"Failed to send message. HTTP status code: {response.status_code}")
