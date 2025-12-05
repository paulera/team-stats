#!/usr/bin/env python3
"""
Slack Emoji Reactions Counter
Retrieves and counts reaction emojis used in a Slack channel.
"""

import os
import sys
import argparse
from collections import Counter
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def get_channel_id(client, channel_name):
    """Get channel ID from channel name."""
    try:
        # Remove # prefix if present
        channel_name = channel_name.lstrip('#')
        
        # List all channels the user is a member of
        cursor = None
        
        while True:
            result = client.users_conversations(
                types="public_channel,private_channel",
                limit=200,
                cursor=cursor
            )
            
            for channel in result['channels']:
                if channel['name'] == channel_name:
                    return channel['id']
            
            # Check if there are more channels
            if not result.get('has_more'):
                break
            
            cursor = result['response_metadata']['next_cursor']
        
        print(f"Error: Channel '{channel_name}' not found or you don't have access to it", file=sys.stderr)
        return None
    
    except SlackApiError as e:
        print(f"Error fetching channels: {e.response['error']}", file=sys.stderr)
        return None


def get_emoji_reactions(client, channel_id, date_from=None, date_to=None):
    """Retrieve all emoji reactions from a channel."""
    emoji_counter = Counter()
    
    try:
        # Convert dates to timestamps if provided
        oldest = date_from.timestamp() if date_from else None
        latest = date_to.timestamp() if date_to else None
        
        # Get channel history
        cursor = None
        
        while True:
            params = {
                'channel': channel_id,
                'limit': 200,
                'cursor': cursor
            }
            
            if oldest:
                params['oldest'] = oldest
            if latest:
                params['latest'] = latest
            
            result = client.conversations_history(**params)
            
            # Process messages
            for message in result['messages']:
                if 'reactions' in message:
                    for reaction in message['reactions']:
                        emoji_counter[reaction['name']] += reaction['count']
            
            # Check if there are more messages
            if not result.get('has_more'):
                break
            
            cursor = result['response_metadata']['next_cursor']
        
        return emoji_counter
    
    except SlackApiError as e:
        print(f"Error fetching messages: {e.response['error']}", file=sys.stderr)
        return None


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Count emoji reactions in a Slack channel')
    parser.add_argument('channel_name', help='Slack channel name')
    parser.add_argument('-df', '--date-from', dest='date_from', help='Start date (YYYY-MM-DD)')
    parser.add_argument('-dt', '--date-to', dest='date_to', help='End date (YYYY-MM-DD)')
    parser.add_argument('-t', '--top', type=int, dest='top', help='Show only top N results (highest to lowest)')
    
    args = parser.parse_args()
    
    # Parse dates if provided
    date_from = None
    date_to = None
    
    try:
        if args.date_from:
            date_from = datetime.strptime(args.date_from, '%Y-%m-%d')
        if args.date_to:
            # Set to end of day
            date_to = datetime.strptime(args.date_to, '%Y-%m-%d')
            date_to = date_to.replace(hour=23, minute=59, second=59)
    except ValueError as e:
        print(f"Error: Invalid date format. Use YYYY-MM-DD", file=sys.stderr)
        sys.exit(1)
    
    # Get Slack token from environment
    slack_token = os.environ.get('SLACK_TOKEN')
    if not slack_token:
        print("Error: SLACK_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    # Initialize Slack client
    client = WebClient(token=slack_token)
    
    # Get channel ID
    channel_id = get_channel_id(client, args.channel_name)
    if not channel_id:
        sys.exit(1)
    
    # Get emoji reactions
    print(f"Fetching emoji reactions from #{args.channel_name}...", file=sys.stderr)
    emoji_counter = get_emoji_reactions(client, channel_id, date_from, date_to)
    
    if emoji_counter is None:
        print("Error: Failed to retrieve emoji reactions", file=sys.stderr)
        sys.exit(1)
    
    # Display results
    sorted_results = sorted(emoji_counter.items(), key=lambda x: x[1])
    
    # Apply top filter if specified (reverse order for top results)
    if args.top:
        sorted_results = sorted_results[-args.top:][::-1]
    
    for emoji, count in sorted_results:
        print(f"{count} :{emoji}:")


if __name__ == "__main__":
    main()
