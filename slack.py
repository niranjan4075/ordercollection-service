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
				"text": "You have a new request:\n*<fakeLink.toEmployeeProfile.com|Fred Enriquez - New device request>*"
			}
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*Type:*\nComputer (laptop)"
				},
				{
					"type": "mrkdwn",
					"text": "*When:*\nSubmitted Aut 10"
				},
				{
					"type": "mrkdwn",
					"text": "*Last Update:*\nMar 10, 2015 (3 years, 5 months)"
				},
				{
					"type": "mrkdwn",
					"text": "*Reason:*\nAll vowel keys aren't working."
				},
				{
					"type": "mrkdwn",
					"text": "*Specs:*\n\"Cheetah Pro 15\" - Fast, really fast\""
				}
			]
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"emoji": true,
						"text": "Approve"
					},
					"style": "primary",
					"value": "click_me_123"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"emoji": true,
						"text": "Deny"
					},
					"style": "danger",
					"value": "click_me_123"
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
