#IMPORT
import logging as log
import time

#CONFIG
log.basicConfig(level=log.INFO) # Set base log level
SLACK_PAGINATION_LIMIT = 30 # Pagination limit for Slack 'list_users'
API_DELAY_MS = 100 # Delay in between API calls (because we're making multiple requests, and do not want to exceed rate limits)
API_TIMEOUT = 60 # Timeout for API calls in seconds

def delayed_api(func):
    def wrapper(*args, **kwargs):
        if API_DELAY_MS:
            time.sleep(API_DELAY_MS / 1000.0)
        return func(*args, **kwargs)

    return wrapper

def get_slack_details(client):
    """Returns a dict of all users (not bots, with email IDs) for a given workspace
    (as authenticated by SLACK_BOT_TOKEN)

    Args:
        client: slack.web.client.WebClient
            Slack WebClient module which is already authenticated
    Returns:
        dict
            Returns a dict, where the keys are 'emails' and values are tuples of Slack usernames
            (which can be tagged with `@`) and Slack IDs
    """

    # Helper method to call a page of users
    @delayed_api
    def _get_active_users(client, next_cursor=None):
        log.debug("Getting next {} members...".format(SLACK_PAGINATION_LIMIT))
        response = client.users_list(limit=SLACK_PAGINATION_LIMIT, cursor=next_cursor)
        users = response["members"]
        response_metadata = response["response_metadata"]

        # Format email:slack_id object if user is active and has an email
        return {u['profile']['email']: (u['name'], u['id']) for u in users if
                not u['is_bot'] and not u['deleted'] and 'email' in u['profile']}, response_metadata['next_cursor']

    active_users, next_cursor = _get_active_users(client)

    # Check if next page available, and update users
    while next_cursor:
        next_active_users, next_cursor = _get_active_users(client, next_cursor)
        active_users.update(next_active_users)
    return active_users