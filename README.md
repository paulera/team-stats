# Team Stats

Simple Python scripts for gathering team statistics from Slack.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Slack token:
```bash
export SLACK_TOKEN=xoxp-your-token-here
```

## Scripts

### slack-list-emojis.py

List emoji reactions used in a Slack channel with their counts.

**Usage:**
```bash
python slack-list-emojis.py <channel_name> [options]
```

**Options:**
- `-df, --date-from YYYY-MM-DD` - Filter from start date
- `-dt, --date-to YYYY-MM-DD` - Filter until end date
- `-t, --top N` - Show only top N results (highest to lowest)

**Examples:**
```bash
# All emoji reactions in a channel
python slack-list-emojis.py general

# Reactions from December 2025
python slack-list-emojis.py general -df 2025-12-01 -dt 2025-12-31

# Reactions since Jan 2025
python slack-list-emojis.py general -df 2025-01-01

# Top 10 most used emojis
python slack-list-emojis.py general -t 10
```

**Output format:**
```
5 :thumbsup:
12 :rocket:
23 :tada:
```

### slack-msg-count.py

Count messages and replies in a Slack channel, with optional per-user breakdown.

**Usage:**
```bash
python slack-msg-count.py <channel_name> [options]
```

**Options:**
- `-r, --replies` - Count only replies
- `-m, --messages` - Count only messages (not replies)
- `-u, --user` - Show counts per user
- `-df, --date-from YYYY-MM-DD` - Filter from start date
- `-dt, --date-to YYYY-MM-DD` - Filter until end date
- `-t, --top N` - Show only top N results (highest to lowest)

**Examples:**
```bash
# Total messages in a channel
python slack-msg-count.py general

# Only replies
python slack-msg-count.py general -r

# Messages per user
python slack-msg-count.py general -u

# Top 5 most active users (replies only)
python slack-msg-count.py general -u -r -t 5

# Messages in November 2025
python slack-msg-count.py general -df 2025-11-01 -dt 2025-11-30
```

**Output format:**
```
142 general
15 general:john@example.com:U12345
8 general:JiraBot:B67890
```

## Notes

- All scripts send status messages to stderr, so you can pipe the output without noise
- Results are sorted in ascending order by default (lowest to highest)
- Use `-t/--top` to get descending order (highest to lowest) with a limit
- Channel names work with or without the `#` prefix
- Scripts only access channels you're a member of

## Piping Examples

```bash
# Get top 5 emojis and save to file
python slack-list-emojis.py general -t 5 > top_emojis.txt

# Count messages and feed to another tool
python slack-msg-count.py general -u | sort -n | tail -10
```
