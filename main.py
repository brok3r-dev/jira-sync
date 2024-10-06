# IMPORT
import configparser
import logging as log
import sys

from slack import WebClient
from modules import slack_api
from modules import jira_api

# CONFIG
log.basicConfig(level=log.INFO) # Set base log level


if __name__ == "__main__":
    args = configparser.ConfigParser()
    args.read('config.ini')

    slack_token = args['DEFAULT']['SLACK_TOKEN']
    jira_url = args['DEFAULT']['JIRA_URL']
    username = args['DEFAULT']['USERNAME']
    jira_apikey = args['DEFAULT']['APIKEY']

    # Gather list of slack users associated with slack token's workspace
    slack_client = WebClient(token=slack_token)
    slack_users = slack_api.gather_slack_details(slack_client)
    total_users = len(slack_users)
    if not slack_users:
        log.warning("No user found for the given Slack workspace associated with token. Exiting!")
        sys.exit(0)

    # Create a new JIRA Web Client
    jira = jira_api.JIRA(jira_url, username, jira_apikey)

    log.info("Looking up {} users in Jira server: {}".format(total_users, jira_url))
    properties_updated = 0
    accounts_found = 0

    for email, slack_info in slack_users.items():
        # Search user by email
        slack_username, slack_id = slack_info
        account_id = jira.get_user(email)
        if account_id:
            accounts_found += 1
            log.info("Found account ID: {} for user: {}".format(account_id, email))
            # Update user property
            if jira.set_user_property(account_id, slack_username, slack_id):
                properties_updated += 1

    log.info("Finished updating {} propertie(s) in {} account(s) found in Jira (Total {} Slack member(s))".format(properties_updated, accounts_found, total_users))
