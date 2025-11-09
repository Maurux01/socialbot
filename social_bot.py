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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Raised when there are configuration-related errors."""
    pass

class PostError(Exception):
    """Raised when there are errors related to posting content."""
    pass

class SocialBot:
    """A class to manage social media interactions."""
    
    def __init__(self, config_path: str = 'config.json'):
        """Initialize the SocialBot with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.client = self._connect_to_mastodon()
        
    def _load_config(self) -> Dict:
        """Load and validate configuration from file or environment variables.
        
        Returns:
            Dict: Configuration dictionary
        
        Raises:
            ConfigError: If configuration is invalid or missing
        """
        # Try environment variables first
        if 'MASTODON_ACCESS_TOKEN' in os.environ and 'MASTODON_API_URL' in os.environ:
            config = {
                'mastodon': {
                    'access_token': os.environ['MASTODON_ACCESS_TOKEN'],
                    'api_base_url': os.environ['MASTODON_API_URL']
                }
            }
            logger.info("Using configuration from environment variables")
            return config
            
        # Fall back to config file
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            # Validate configuration
            if not config.get('mastodon'):
                raise ConfigError("Missing 'mastodon' configuration section")
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