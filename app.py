import os
import time
import tempfile
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.app import App
from dotenv import load_dotenv

load_dotenv(".env")

import config
from utils.log import setup_logger
from cluster.node import get_node_info, get_squeue
from cluster.query_slurm import get_slurm_version

logger = setup_logger(output=config.LOGGER_OUTPUT, level=config.LOGGER_LEVEL)

app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    logger=logger,
)

@app.command("/cluster")
def cluster_command(ack, say):
    """
    Handles the /cluster command to display basic Slurm node information.
    """
    start = time.time() * 1000
    ack()
    node_info = get_node_info()
    output = f"```\n{node_info}\n```\n\n"
    output += f"Execution time: {((time.time() * 1000) - start):.2f} milliseconds"
    say(output)
    
@app.command("/squeue")
def squeue_command(ack, command, say, client):
    # TODO: Hide command when not in channel or handle errors otherwise
    
    start = time.time() * 1000
    ack()
    
    user_id = command['user_id']
    username = command.get("text")
    result = client.users_info(user=user_id)
    user = result["user"]
    real_name = user.get("real_name")
    
    squeue = get_squeue(real_name, username=username)

    with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmp:
        tmp.write(squeue)
        tmp_name = tmp.name
    
    client.files_upload_v2(
        channel=command['channel_id'],
        title="Job Queue Information",
        filename="squeue_results.txt",
        file=tmp_name,
        initial_comment="Here's your job queue information:"
    )
    say(f"Execution time: {((time.time() * 1000) - start):.2f} milliseconds")
    
@app.command("/version")
def get_my_id(ack):
    ack(text=f"Current version of SLURM is {get_slurm_version()}")
    
@app.command("/myid")
def get_my_id(ack, body):
    user_id = body["user_id"]
    ack(text=f"Your Slack User ID is: {user_id}")
    
@app.command("/debug")
def handle_command(ack, say, command, client):
    ack()
    user_id = command['user_id']
    if not user_id == os.environ["PERSONAL_SLACK_USER_ID"]:
        say("Invalid permissions")
    try:
        result = client.users_info(user=user_id)
        user = result["user"]
        real_name = user.get("real_name")
        username = user.get("name")
        logger.info(f"Real name: {real_name}, Username: {username}")
        client.chat_postMessage(
            channel=command['channel_id'],
            text=f"Hello {real_name} (@{username})!"
        )
    except Exception as e:
        logger.error(f"Error fetching user info: {e}")

if __name__ == "__main__":
    SocketModeHandler(app, app_token=os.environ["SLACK_APP_TOKEN"]).start()