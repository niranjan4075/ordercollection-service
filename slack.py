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
            "text": {
                "type": "mrkdwn",
                "text": "Danny Torrence left the following review for your property:"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "<https://example.com|Overlook Hotel> \n :star: \n Doors had too many axe holes, guest in room " +
                    "237 was far too rowdy, whole place felt stuck in the 1920s."
            },
            {
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Farmhouse",
						"emoji": true
					},
					"value": "click_me_123"
				},
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*Average Rating*\n1.0"
                }
            ]
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
