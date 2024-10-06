#IMPORT
import logging as log
import time
import requests
import json

from urllib import parse

#CONFIG
log.basicConfig(level=log.INFO) # Set base log level
API_DELAY_MS = 100 # Delay in between API calls (because we're making multiple requests, and do not want to exceed rate limits)
API_TIMEOUT = 60 # Timeout for API calls in seconds

def delayed_api(func):
    """Decorator to add a delay in between API calls
    """

    def wrapper(*args, **kwargs):
        log.debug("Delaying API call by {}ms".format(API_DELAY_MS))
        if API_DELAY_MS:
            time.sleep(API_DELAY_MS / 1000.0)
        return func(*args, **kwargs)

    return wrapper

class JIRA(object):
    _SEARCH_PATH = "rest/api/3/user/search"
    _PROPERTY_PATH = "rest/api/3/user/properties/"
    _HEADERS = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    def _wrap_error(self, error_message, response):
        """Helper to log HTTPResponse errors
        """
        log.error("{} [{}] {}".format(error_message, response.status_code, response.json()))

    def __init__(self, server_url, username, api_token):
        """Create a new JIRA Webclient

        Args:
            server_url: str
                JIRA server side URL
            username: str
                Atlassian account email (`@atlassian.com`) associated with JIRA server
            api_token: str
                User API token generated from `https://id.atlassian.com/manage/api-tokens`
        """
        self.server_url = server_url
        self.username = username
        self.api_token = api_token
        self.search_url = parse.urljoin(self.server_url, self._SEARCH_PATH)
        self.property_url = parse.urljoin(self.server_url, self._PROPERTY_PATH)

    @delayed_api
    def get_user(self, email):
        """Search for a user by e-mail and return the account ID if found

        Args:
            email: str
                Email ID pattern to search user with

        Returns:
            str/None
                Return the account ID of the user if found in JIRA server, else return None

        """
        response = requests.get(self.search_url,
                                auth=(self.username, self.api_token),
                                headers=self._HEADERS,
                                params={'query': email, 'maxResults': 1},
                                timeout=API_TIMEOUT)
        if response:
            json_response = response.json()
            if len(json_response) > 0:
                return json_response[0]['accountId']
            log.warning("No user found for email: {}".format(email))
        else:
            self._wrap_error("Failed to call search API.", response)

    @delayed_api
    def set_user_property(self, account_id, slack_username, slack_id, key='metadata'):
        """Set user property (slack_id) for a given account ID in the JIRA server

        Args:
            account_id: str
                Account ID of the user
            slack_username: str
                Slack username (which can be tagged)
            slack_id: str
                Slack ID of the user
            key: str (Optional, defaults to 'metadata')
                Path where the user property is updated

        Returns:
            bool
                Returns True on successful property update, False otherwise

        """
        response = requests.put(parse.urljoin(self.property_url, key),
                                auth=(self.username, self.api_token),
                                headers=self._HEADERS,
                                params={'accountId': account_id},
                                data=json.dumps({'slack_username': slack_username, 'slack_id': slack_id}),
                                timeout=API_TIMEOUT)
        if not response:
            self._wrap_error("Could not add property for account: {}".format(account_id), response)
            return False
        else:
            log.info("User property `metadata.value.slack_id:{}, metadata.value.slack_username:{}` set for {}".format(
                slack_id, slack_username, account_id))
            return True

    def get_slack_info(self, account_id):
        """Get slack username, slack ID property values (under {account_id}/properties/metadata) if set for user

        Args:
            account_id: str
                Account ID of the user

        Returns:
            tuple(str, str)
                (Taggable Slack username of the user, Slack ID) if found

        """
        response = requests.get(parse.urljoin(self.property_url, 'metadata'),
                                auth=(self.username, self.api_token),
                                headers=self._HEADERS,
                                params={'accountId': account_id},
                                timeout=API_TIMEOUT)
        if response:
            json_response = response.json()
            metadata_value = json_response['value']
            if 'slack_id' in metadata_value and 'slack_username' in metadata_value:
                return metadata_value['slack_id'], metadata_value['slack_username']
        self._wrap_error("Could not find a slack_id/slack_username property for account: {}".format(account_id),
                         response)