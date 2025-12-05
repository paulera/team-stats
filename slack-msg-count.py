#!/usr/bin/env python3
"""
Slack Message Counter
Counts messages and replies in a Slack channel, optionally per user.
"""

import os
import sys
import argparse
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
        
        return None
    
    except SlackApiError as e:
        return None


def get_user_display(client, user_id, is_bot, user_cache):
    """Get user display name from user ID, with caching."""
    if user_id in user_cache:
        return user_cache[user_id]
    
    try:
        if is_bot:
            # For bots, try to get bot info
            result = client.bots_info(bot=user_id)
            bot_name = result['bot'].get('name', user_id)
            display = f"{bot_name}:{user_id}"
        else:
            # For users, get email
            result = client.users_info(user=user_id)
            email = result['user']['profile'].get('email', user_id)
            display = f"{email}:{user_id}"
        
        user_cache[user_id] = display
        return display
    except SlackApiError as e:
        # Fallback to just the ID
        display = f"{user_id}:{user_id}"
        user_cache[user_id] = display
        return display


def count_messages(client, channel_id, channel_name, count_replies, count_messages, per_user, date_from=None, date_to=None):
    """Count messages and/or replies in a channel."""
    try:
        # Convert dates to timestamps if provided
        oldest = date_from.timestamp() if date_from else None
        latest = date_to.timestamp() if date_to else None
        
        # Initialize counters
        total_count = 0
        user_counts = {}
        user_is_bot = {}
        user_cache = {}
        
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
                # Get user identifier and check if it's a bot
                user_id = message.get('user')
                is_bot = False
                
                if not user_id:
                    # Check for bot_id or app_id
                    user_id = message.get('bot_id') or message.get('app_id')
                    is_bot = True
                
                if not user_id:
                    user_id = 'unknown'
                    is_bot = True
                
                is_reply = 'thread_ts' in message and message.get('thread_ts') != message.get('ts')
                
                # Count based on filters
                should_count = False
                if count_replies and count_messages:
                    should_count = True
                elif count_replies and is_reply:
                    should_count = True
                elif count_messages and not is_reply:
                    should_count = True
                elif not count_replies and not count_messages:
                    should_count = True
                
                if should_count:
                    total_count += 1
                    if per_user:
                        if user_id not in user_counts:
                            user_counts[user_id] = 0
                            user_is_bot[user_id] = is_bot
                        user_counts[user_id] += 1
            
            # Check if there are more messages
            if not result.get('has_more'):
                break
            
            cursor = result['response_metadata']['next_cursor']
        
        # Format output
        if per_user:
            results = []
            for user_id, count in user_counts.items():
                display = get_user_display(client, user_id, user_is_bot[user_id], user_cache)
                results.append((count, f"{channel_name}:{display}"))
            return results
        else:
            return [(total_count, channel_name)]
    
    except SlackApiError as e:
        return None


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Count messages in a Slack channel')
    parser.add_argument('channel_name', help='Slack channel name')
    parser.add_argument('-r', '--replies', action='store_true', help='Count only replies')
    parser.add_argument('-m', '--messages', action='store_true', help='Count only messages (not replies)')
    parser.add_argument('-u', '--user', action='store_true', help='Show counts per user')
    parser.add_argument('-df', '--date-from', dest='date_from', help='Start date (YYYY-MM-DD)')
    parser.add_argument('-dt', '--date-to', dest='date_to', help='End date (YYYY-MM-DD)')
    
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
    except ValueError:
        sys.exit(1)
    
    # Get Slack token from environment
    slack_token = os.environ.get('SLACK_TOKEN')
    if not slack_token:
        sys.exit(1)
    
    # Initialize Slack client
    client = WebClient(token=slack_token)
    
    # Get channel ID
    channel_id = get_channel_id(client, args.channel_name)
    if not channel_id:
        sys.exit(1)
    
    # Count messages
    print(f"Counting messages in #{args.channel_name}...", file=sys.stderr)
    results = count_messages(
        client, 
        channel_id, 
        args.channel_name,
        args.replies, 
        args.messages, 
        args.user,
        date_from, 
        date_to
    )
    
    if results is None:
        sys.exit(1)
    
    # Display results
    for count, label in results:
        print(f"{count} {label}")


if __name__ == "__main__":
    main()