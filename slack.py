import os
import ssl
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load Slack token from environment variable
slack_token = os.getenv("SLACK_BOT_TOKEN")
if not slack_token:
    raise ValueError("SLACK_BOT_TOKEN environment variable not set.")

# Initialize Slack client with correct SSL handling
client = WebClient(token=slack_token, ssl=ssl.create_default_context())

def send_message_to_slack(message, channel):
    """
    Sends a message to a specified Slack channel.
    
    Args:
        message (str): The message content.
        channel (str): The Slack channel ID or name.
    """
    try:
        response = client.chat_postMessage(
            channel=channel,
            text=message
        )
        print("Message sent successfully:", response["ts"])
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

# Example Usage
if __name__ == "__main__":
    send_message_to_slack("Hello, Slack!", "#general")  # Replace #general with your channel ID
