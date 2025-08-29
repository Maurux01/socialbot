'''
A simple bot to post to social media.
'''

import json
import sys
from mastodon import Mastodon

CONFIG_FILE = 'config.json'

def load_config():
    '''Loads configuration from config.json.'''
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {CONFIG_FILE} not found. Please create it from config.json.example.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode {CONFIG_FILE}. Please check its format.")
        sys.exit(1)

def connect_to_mastodon(config):
    '''Connects to Mastodon using credentials from the config.'''
    try:
        mastodon_config = config['mastodon']
        client = Mastodon(
            access_token=mastodon_config['access_token'],
            api_base_url=mastodon_config['api_base_url']
        )
        # Check if credentials are valid
        client.account_verify_credentials()
        print("Successfully connected to Mastodon.")
        return client
    except KeyError:
        print("Error: 'mastodon' configuration is missing in config.json.")
        sys.exit(1)
    except Exception as e:
        print(f"Error connecting to Mastodon: {e}")
        sys.exit(1)

def post_toot(client, content):
    '''Posts a toot to Mastodon.'''
    try:
        client.toot(content)
        print(f"Successfully posted to Mastodon: {content}")
    except Exception as e:
        print(f"Error posting to Mastodon: {e}")

if __name__ == '__main__':
    config = load_config()
    mastodon_client = connect_to_mastodon(config)
    
    if mastodon_client:
        # This is a test post. You can change this content.
        post_toot(mastodon_client, "Hello world from my Python bot! #bot")