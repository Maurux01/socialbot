# Social Bot

This bot syncs posts from a Twitter (X) account to Mastodon and Bluesky.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure:**
    - Rename `config.json.example` to `config.json`.
    - Fill in your API keys and access tokens for Twitter, Mastodon, and Bluesky.

3.  **Run:**
    ```bash
    python social_bot.py
    ```

## How it Works

- The script runs in a loop, checking for new tweets from the specified user.
- It stores the ID of the last tweet it processed in `last_tweet_id.txt` to avoid duplicate posts.
- When a new tweet is found, it posts the content to the configured Mastodon and Bluesky accounts.