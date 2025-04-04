import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import pwd

from utils.log import get_logger
from utils.utils import cache_for_n_seconds

logger = get_logger(__name__)


def get_slack_users():
    client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

    try:
        # Call the users.list method using the WebClient
        # users.list requires the users:read scope
        result = client.users_list()["members"]
        return result

    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))
        return []


@cache_for_n_seconds(seconds=24 * 60 * 60)
def get_slack2unix_map():
    hardcoded_map = {
        "U07BESQTQM6": "ramirezc",
        "U086DUX6V4Y": "kresgeb"
    }
    logger.info("Using hardcoded mapping in get_slack2unix_map")
    logger.info("Starting get_slack2unix_map")
    slack2unix_map = hardcoded_map.copy()
    # slack_users = get_slack_users()
    # for linux_user in pwd.getpwall():
    #     if linux_user.pw_uid < 100 or linux_user.pw_name.startswith('.'):
    #         continue
    #     # Get the GECOS field - this is the 5th field in /etc/passwd
    #     linux_gecos = linux_user.pw_gecos
        
    #     for slack_user in slack_users:
    #         if slack_user['id'] == 'U01UCDZ1RT3':
    #             continue
    #         if 'real_name' in slack_user:
    #             # Debug log to see what's being compared
    #             logger.debug(f"Comparing - Slack: '{slack_user['real_name']}' with Unix: '{linux_gecos}'")
                
    #             # Perform exact matching - the real_name must be exactly the same as the GECOS field
    #             if slack_user['real_name'] == linux_gecos:
    #                 # Found exact match - add to mapping
    #                 slack2unix_map[slack_user['id']] = linux_user.pw_name
    #                 logger.info(f"Exact match found - Slack: {slack_user['real_name']} -> Unix: {linux_user.pw_name}")
    return slack2unix_map
