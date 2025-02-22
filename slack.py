import os
import requests
import json
import certifi

# Load Slack token securely from environment variable
slack_token = os.getenv("SLACK_BOT_TOKEN")
if not slack_token:
    raise ValueError("SLACK_BOT_TOKEN environment variable not set.")

# Slack API URL
SLACK_API_URL = "https://slack.com/api/chat.postMessage"

def send_message_to_slack(message, channel):
    """
    Sends a message to a specified Slack channel using requests.

    Args:
        message (str): The message content.
        channel (str): The Slack channel ID or name.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {slack_token}"
    }
    
    payload = {
        "channel": channel,
        "text": message
    }

    try:
        response = requests.post(
            SLACK_API_URL,
            headers=headers,
            data=json.dumps(payload),
            verify=certifi.where()  # Use certifi for SSL verification
        )
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get("ok"):
            print("Message sent successfully:", response_data["ts"])
        else:
            print(f"Error sending message: {response_data.get('error')}")
    
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

# Example Usage
if __name__ == "__main__":
    send_message_to_slack("Hello, Slack! Sent using requests.", "#general")  # Replace #general with your channel ID
