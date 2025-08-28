
import os
import json
import time
import tweepy
from mastodon import Mastodon
from atproto import Client

def load_config():
    """Loads configuration from config.json."""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found. Please create it based on config.json.example.")
        exit(1)
    except json.JSONDecodeError:
        print("Error: Could not decode config.json. Please check its format.")
        exit(1)

def get_last_tweet_id():
    """Gets the most recently processed tweet ID from a file."""
    if not os.path.exists('last_tweet_id.txt'):
        return None
    with open('last_tweet_id.txt', 'r') as f:
        return f.read().strip()

def save_last_tweet_id(tweet_id):
    """Saves the latest processed tweet ID to a file."""
    with open('last_tweet_id.txt', 'w') as f:
        f.write(str(tweet_id))

def fetch_latest_tweet(config, since_id):
    """
    Fetches the latest tweet from the specified user using Tweepy.
    Note: Requires elevated or v2 API access.
    """
    print("Fetching latest tweet...")
    try:
        client = tweepy.Client(
            bearer_token=config['twitter']['bearer_token'],
            consumer_key=config['twitter']['api_key'],
            consumer_secret=config['twitter']['api_secret_key'],
            access_token=config['twitter']['access_token'],
            access_token_secret=config['twitter']['access_token_secret']
        )
        user = client.get_user(username=config['twitter']['username'])
        user_id = user.data.id
        
        # Using since_id to get tweets since the last processed one
        response = client.get_users_tweets(user_id, since_id=since_id, max_results=5)
        
        if response.data:
            # Tweets are returned in reverse chronological order, so the first one is the newest
            return response.data[0]
    except Exception as e:
        print(f"Error fetching from Twitter: {e}")
    return None

def post_to_mastodon(config, text):
    """Posts a status to Mastodon."""
    print(f"Posting to Mastodon: {text}")
    try:
        mastodon = Mastodon(
            access_token=config['mastodon']['access_token'],
            api_base_url=config['mastodon']['api_base_url']
        )
        mastodon.status_post(text)
        print("Successfully posted to Mastodon.")
    except Exception as e:
        print(f"Error posting to Mastodon: {e}")

def post_to_bluesky(config, text):
    """Posts a status to Bluesky."""
    print(f"Posting to Bluesky: {text}")
    try:
        client = Client()
        client.login(config['bluesky']['handle'], config['bluesky']['app_password'])
        client.send_post(text)
        print("Successfully posted to Bluesky.")
    except Exception as e:
        print(f"Error posting to Bluesky: {e}")

def main():
    """Main loop to check for new tweets and post them."""
    config = load_config()
    check_interval_seconds = config.get('check_interval_seconds', 300)

    print("Social Bot started. Checking for new tweets...")

    while True:
        last_processed_id = get_last_tweet_id()
        
        latest_tweet = fetch_latest_tweet(config, last_processed_id)

        if latest_tweet and str(latest_tweet.id) != last_processed_id:
            print(f"New tweet found: {latest_tweet.text}")
            
            post_to_mastodon(config, latest_tweet.text)
            post_to_bluesky(config, latest_tweet.text)
            
            save_last_tweet_id(latest_tweet.id)
        else:
            print("No new tweets found.")

        print(f"Waiting for {check_interval_seconds} seconds before next check...")
        time.sleep(check_interval_seconds)

if __name__ == "__main__":
    main()
