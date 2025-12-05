# Team Stats - Project Context

## Project Overview
A suite of simple Python scripts for daily team statistics gathering. The scripts are designed for maximum simplicity to ensure easy maintenance by humans.

## Core Principles
1. **Simplicity First**: Keep scripts as simple as possible. No unnecessary abstractions or frameworks.
2. **Single Responsibility**: Each script does one thing well.
3. **Environment Variables**: Sensitive tokens and credentials come from environment variables.
4. **Clean Output**: Scripts output only essential data to stdout, status messages go to stderr.
5. **Zero Verbosity to stdout**: Only machine-readable data goes to stdout (for piping). All human-readable messages (status, errors, progress) go to stderr.
6. **Pipe-Friendly**: Output is designed to be piped into other programs without noise.
7. **Date Filtering by Default**: Any script that retrieves time-based data must support `-df/--date-from` and `-dt/--date-to` parameters out of the box.

## Code Style Guidelines
- Use Python 3 with standard library where possible
- Use argparse for command-line arguments
- Short flags use single dash (e.g., `-df`), long flags use double dash (e.g., `--date-from`)
- Functions should have clear docstrings
- Error handling: return None on errors, print error messages to stderr in main() before exiting
- Use descriptive variable names
- Keep functions focused and small

## Output Format Standards
All scripts that produce counting results must follow these conventions:
- **Count comes first**: Format is `count item` (e.g., `42 :thumbsup:` or `15 channel-name:user@email.com`)
- **Ascending order by default**: Results sorted from lowest to highest count
- **Top N results**: When `-t/--top` parameter is used, show only the top N results in descending order (highest to lowest)
- **Clean output**: Only data goes to stdout, status messages go to stderr
- **Pipe-friendly**: No headers, borders, or extra formatting that interferes with piping

## Scripts

### slack-list-emojis.py
**Purpose**: Retrieve and count reaction emojis from a Slack channel.

**Environment Variables**:
- `SLACK_TOKEN`: Slack API token (format: `xoxp-...`)

**Arguments**:
- `channel_name` (positional): Slack channel name (with or without `#` prefix)
- `-df, --date-from`: Start date in YYYY-MM-DD format (optional)
- `-dt, --date-to`: End date in YYYY-MM-DD format (optional, includes full day until 23:59:59)
- `-t, --top`: Show only top N results in descending order (optional)

**Output Format**:
```
count :emoji_name:
```
Sorted ascending by count (most used at the end). Use `-t N` to show only top N results in descending order.

**Dependencies**: `slack-sdk>=3.19.0`

**Key Features**:
- Accesses channels the user is a member of (public and private)
- Supports date filtering via Slack API timestamps
- Pagination handles large message histories
- Status message sent to stderr for pipe compatibility

**Implementation Notes**:
- Uses `users_conversations` to get channels user has access to
- Uses `conversations_history` with cursor-based pagination
- Date filtering uses `oldest` and `latest` parameters as Unix timestamps
- Reactions are aggregated using Counter from collections

### slack-msg-count.py
**Purpose**: Count messages and replies in a Slack channel, optionally per user.

**Environment Variables**:
- `SLACK_TOKEN`: Slack API token (format: `xoxp-...`)

**Arguments**:
- `channel_name` (positional): Slack channel name (with or without `#` prefix)
- `-r, --replies`: Count only replies (optional)
- `-m, --messages`: Count only messages, not replies (optional)
- `-u, --user`: Show counts per user (optional)
- `-df, --date-from`: Start date in YYYY-MM-DD format (optional)
- `-dt, --date-to`: End date in YYYY-MM-DD format (optional, includes full day until 23:59:59)
- `-t, --top`: Show only top N results in descending order (optional)

**Output Format**:
```
count channel-name
count channel-name:email:user_id
count channel-name:BotName:bot_id
```
Sorted ascending by count (highest at the end). Use `-t N` to show only top N results in descending order.

**Dependencies**: `slack-sdk>=3.19.0`

**Key Features**:
- Counts all messages by default (both messages and replies)
- Can filter to count only replies (`-r`) or only messages (`-m`)
- Can break down counts per user (`-u`)
- Distinguishes between human users (shown as `email:user_id`) and bots/workflows (shown as `BotName:bot_id`)
- Supports combining flags (e.g., `-u -r` for replies per user)
- Supports date filtering via Slack API timestamps
- Pagination handles large message histories
- Status message sent to stderr for pipe compatibility

**Implementation Notes**:
- Uses `users_conversations` to get channels user has access to
- Uses `conversations_history` with cursor-based pagination
- Identifies bots/workflows by absence of `user` field (uses `bot_id` or `app_id` instead)
- Uses `users_info` to get user emails and `bots_info` to get bot names
- Date filtering uses `oldest` and `latest` parameters as Unix timestamps
- Reply detection: message has `thread_ts` that differs from its own `ts`

## Dependencies
All dependencies are listed in `requirements.txt`. Keep dependencies minimal.

## Future Scripts
When adding new scripts:
1. Follow the naming pattern: `{source}-{action}-{resource}.py`
2. Use same argument style (`-xy` and `--extended-name`)
3. Environment variables for credentials
4. Document in this file with same level of detail
5. Add dependencies to `requirements.txt`
6. Keep output clean and pipe-friendly
7. Follow output format standards (count first, ascending order by default, support `-t/--top`)
8. **Always include date filtering**: Add `-df/--date-from` and `-dt/--date-to` parameters for any script that retrieves time-based data
9. Update README.md with script description and examples

## Testing Approach
Scripts should be testable by running them directly. No formal test framework needed unless complexity increases significantly. Manual testing with real API calls is acceptable given the simplicity requirement.

## Error Handling Pattern
```python
# Functions return None on error, no printing
def some_function():
    try:
        # do work
        return result
    except SomeError:
        return None

# Main checks for None, prints error to stderr, then exits
def main():
    result = some_function()
    if result is None:
        print("Error: Failed to retrieve data", file=sys.stderr)
        sys.exit(1)
```

## Output Pattern
```python
# Status/progress to stderr
print(f"Processing...", file=sys.stderr)

# Data to stdout (for piping)
print(data)
```

## Date Handling Pattern
**Date filtering is a standard feature for all time-based scripts.**

When adding date filters (required for any script retrieving time-based data):
- Always include `-df/--date-from` and `-dt/--date-to` parameters
- Use YYYY-MM-DD format
- Use `datetime.strptime()` for parsing
- Convert to appropriate format for target API (e.g., Unix timestamp for Slack)
- For end dates, set time to 23:59:59 to include full day
- Exit silently on invalid date format
- Both parameters are optional (allow querying all data when not specified)

## Maintenance Notes
- Keep this file updated when adding/modifying scripts
- Update principles if patterns emerge
- Document any non-obvious API quirks or workarounds
- Keep examples current
