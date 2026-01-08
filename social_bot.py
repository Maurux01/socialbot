"""
A sophisticated bot for posting to social media platforms with advanced features.
Supports media uploads, scheduled posts, and thread creation.
"""

import json
import sys
import os
import logging
from typing import Optional, Dict, List, Union
from datetime import datetime
from pathlib import Path
from mastodon import Mastodon

"""SocialBot: small Mastodon posting utility.

This module provides a compact, well-logged `SocialBot` class that
connects to Mastodon, validates configuration (including environment
overrides), and posts statuses with optional media and visibility.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from typing import Optional

from mastodon import Mastodon

CONFIG_FILE = "config.json"

logger = logging.getLogger(__name__)


def load_config(path: str = CONFIG_FILE) -> dict:
    """Load configuration from JSON file and override with environment vars.

    Environment variables `MASTODON_API_BASE_URL` and `MASTODON_ACCESS_TOKEN`
    will override values from the file when present.
    """
    cfg = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except FileNotFoundError:
        logger.warning("Config file %s not found; falling back to environment variables.", path)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in %s: %s", path, e)
        sys.exit(1)

    mastodon_cfg = cfg.get("mastodon", {})

    api_base = os.getenv("MASTODON_API_BASE_URL") or mastodon_cfg.get("api_base_url")
    access_token = os.getenv("MASTODON_ACCESS_TOKEN") or mastodon_cfg.get("access_token")

    if not api_base or not access_token:
        logger.error("Mastodon configuration incomplete. Provide api_base_url and access_token via %s or environment.", path)
        sys.exit(1)

    return {"mastodon": {"api_base_url": api_base, "access_token": access_token}}


class SocialBot:
    """Encapsulates Mastodon client operations."""

    def __init__(self, config: dict) -> None:
        self.config = config
        self.client: Optional[Mastodon] = None

    def connect(self) -> None:
        """Create a Mastodon client and verify credentials."""
        mast_cfg = self.config["mastodon"]
        try:
            self.client = Mastodon(
                access_token=mast_cfg["access_token"], api_base_url=mast_cfg["api_base_url"]
            )
            self.client.account_verify_credentials()
            logger.info("Connected to Mastodon at %s", mast_cfg["api_base_url"])
        except Exception as exc:  # keep broad to surfacing API/client errors
            logger.exception("Failed to connect to Mastodon: %s", exc)
            raise

    def post(self, content: str, visibility: str = "public", media_path: Optional[str] = None) -> None:
        """Post `content` to Mastodon with optional `media_path` and `visibility`.

        `visibility` can be one of: public, unlisted, private, direct.
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() before posting.")

        media_ids = None
        if media_path:
            if not os.path.exists(media_path):
                logger.error("Media file not found: %s", media_path)
                raise FileNotFoundError(media_path)
            try:
                logger.debug("Uploading media: %s", media_path)
                media = self.client.media_post(media_path)
                media_ids = [media["id"]]
            except Exception as exc:
                logger.exception("Failed to upload media: %s", exc)
                raise

        try:
            logger.info("Posting status (visibility=%s): %s", visibility, content)
            self.client.status_post(status=content, media_ids=media_ids, visibility=visibility)
            logger.info("Posted successfully.")
        except Exception as exc:
            logger.exception("Failed to post status: %s", exc)
            raise


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Post a status to Mastodon using SocialBot.")
    parser.add_argument("message", help="Text content to post")
    parser.add_argument("--visibility", default="public", help="Visibility: public/unlisted/private/direct")
    parser.add_argument("--media", help="Path to media file to attach")
    parser.add_argument("--config", default=CONFIG_FILE, help="Path to config.json file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO, format="%(levelname)s: %(message)s")

    config = load_config(args.config)
    bot = SocialBot(config)
    try:
        bot.connect()
        bot.post(args.message, visibility=args.visibility, media_path=args.media)
    except Exception:
        logger.error("Operation failed. See logs for details.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
            if not config['mastodon'].get('access_token'):
                raise ConfigError("Missing Mastodon access token")
            if not config['mastodon'].get('api_base_url'):
                raise ConfigError("Missing Mastodon API URL")
                
            return config
            
        except FileNotFoundError:
            raise ConfigError(f"Configuration file {self.config_path} not found")
        except json.JSONDecodeError:
            raise ConfigError(f"Invalid JSON in configuration file {self.config_path}")
    
    def _connect_to_mastodon(self) -> Mastodon:
        """Establish connection to Mastodon API.
        
        Returns:
            Mastodon: Authenticated Mastodon client instance
            
        Raises:
            ConfigError: If connection fails
        """
        try:
            mastodon_config = self.config['mastodon']
            client = Mastodon(
                access_token=mastodon_config['access_token'],
                api_base_url=mastodon_config['api_base_url']
            )
            # Verify credentials
            client.account_verify_credentials()
            logger.info("Successfully connected to Mastodon")
            return client
            
        except Exception as e:
            raise ConfigError(f"Failed to connect to Mastodon: {str(e)}")
    
    def post(self, content: str, media_files: Optional[List[str]] = None, 
             visibility: str = 'public', scheduled_at: Optional[datetime] = None,
             in_reply_to_id: Optional[str] = None) -> Dict:
        """Post content to Mastodon with optional media attachments.
        
        Args:
            content: The text content to post
            media_files: Optional list of paths to media files to attach
            visibility: Post visibility ('public', 'unlisted', 'private', 'direct')
            scheduled_at: Optional datetime for scheduled posting
            in_reply_to_id: Optional ID of post to reply to
            
        Returns:
            Dict: Response from Mastodon API
            
        Raises:
            PostError: If posting fails
        """
        try:
            # Validate content length
            if len(content) > 500:  # Mastodon's character limit
                raise PostError("Content exceeds Mastodon's character limit of 500")
            
            # Handle media attachments
            media_ids = []
            if media_files:
                for media_file in media_files:
                    if not Path(media_file).exists():
                        raise PostError(f"Media file not found: {media_file}")
                    media = self.client.media_post(media_file)
                    media_ids.append(media['id'])
            
            # Prepare post parameters
            post_params = {
                'status': content,
                'visibility': visibility,
                'media_ids': media_ids if media_ids else None,
                'scheduled_at': scheduled_at,
                'in_reply_to_id': in_reply_to_id
            }
            
            # Remove None values
            post_params = {k: v for k, v in post_params.items() if v is not None}
            
            # Post to Mastodon
            response = self.client.status_post(**post_params)
            logger.info(f"Successfully posted to Mastodon: {content[:50]}...")
            return response
            
        except Exception as e:
            raise PostError(f"Failed to post content: {str(e)}")
    
    def create_thread(self, posts: List[str], visibility: str = 'public') -> List[Dict]:
        """Create a thread of connected posts.
        
        Args:
            posts: List of post contents
            visibility: Visibility level for all posts in thread
            
        Returns:
            List[Dict]: List of responses from Mastodon API
        """
        responses = []
        previous_id = None
        
        for post in posts:
            response = self.post(post, visibility=visibility, in_reply_to_id=previous_id)
            responses.append(response)
            previous_id = response['id']
        
        return responses

def main():
    """Main entry point for the bot."""
    try:
        bot = SocialBot()
        
        # Example usage
        # Simple post
        bot.post("Hello world from my enhanced Python bot! 🤖 #bot")
        
        # Thread creation
        bot.create_thread([
            "1/3 This is the start of a thread!",
            "2/3 Here's the middle part...",
            "3/3 And this is the end!"
        ])
        
    except (ConfigError, PostError) as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()