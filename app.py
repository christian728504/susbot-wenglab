import os
import time

from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.app import App
from dotenv import load_dotenv

load_dotenv(".env")

import config
from utils.log import setup_logger
from cluster.node import get_node_info

logger = setup_logger(output=config.LOGGER_OUTPUT, level=config.LOGGER_LEVEL)

app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    logger=logger,
)

@app.command("/cluster")
def cluster_info(ack, say):
    """
    Handles the /cluster command to display basic Slurm node information.
    """
    start = time.time() * 1000
    ack()
    node_info = get_node_info()
    output = f"```\n{node_info}\n```\n\n"
    output += f"Execution time: {((time.time() * 1000) - start):.2f} milliseconds"
    say(output)
    
@app.command("/myid")
def get_my_id(ack, body):
    user_id = body["user_id"]
    ack(text=f"Your Slack User ID is: {user_id}")

if __name__ == "__main__":
    SocketModeHandler(app, app_token=os.environ["SLACK_APP_TOKEN"]).start()