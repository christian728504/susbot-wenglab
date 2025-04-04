import os
import json
from dotenv import load_dotenv

load_dotenv('.env')

from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.app import App
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("debug_bot")

app = App(token=os.environ["SLACK_BOT_TOKEN"],
          signing_secret=os.environ["SLACK_APP_TOKEN"],
          logger=logger)

@app.command("/hello")
def hello_command(ack, body):
    user_id = body["user_id"]
    logger.info(f"Received /hello command from user {user_id}")
    ack(text=f"Hello <@{user_id}>! I'm alive and responding to commands.")
    
@app.command("/testuser")
def test_user_mapping(ack, body):
    from utils.slack2unix import get_slack2unix_map
    user_id = body["user_id"]
    
    logger.info(f"Testing user mapping for {user_id}")
    ack(text="Checking user mapping... please wait.")
    
    try:
        user_map = get_slack2unix_map()
        unix_user = user_map.get(user_id, None)
        
        if unix_user:
            say = app.client.chat_postMessage
            say(
                channel=body["channel_id"],
                text=f"Found Unix user mapping: {user_id} → {unix_user}"
            )
        else:
            say = app.client.chat_postMessage
            say(
                channel=body["channel_id"],
                text=f"No Unix user mapping found for Slack user {user_id}"
            )
        
        logger.info(f"All user mappings: {json.dumps(user_map, indent=2)}")
    except Exception as e:
        logger.error(f"Error testing user mapping: {str(e)}")
        say = app.client.chat_postMessage
        say(
            channel=body["channel_id"],
            text=f"Error testing user mapping: {str(e)}"
        )

if __name__ == "__main__":
    logger.info("Starting debug bot in socket mode...")
    try:
        SocketModeHandler(app).start()
    except Exception as e:
        logger.error(f"Error starting app: {str(e)}")