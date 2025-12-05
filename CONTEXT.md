# Team Stats - Project Context

## Project Overview
A suite of simple Python scripts for daily team statistics gathering. The scripts are designed for maximum simplicity to ensure easy maintenance by humans.

## Core Principles
1. **Simplicity First**: Keep scripts as simple as possible. No unnecessary abstractions or frameworks.
2. **Single Responsibility**: Each script does one thing well.
3. **Environment Variables**: Sensitive tokens and credentials come from environment variables.
4. **Clean Output**: Scripts output only essential data to stdout, status messages go to stderr.
5. **Zero Verbosity**: Errors exit silently with error codes; no error messages printed.
6. **Pipe-Friendly**: Output is designed to be piped into other programs without noise.

## Code Style Guidelines
- Use Python 3 with standard library where possible
- Use argparse for command-line arguments
- Short flags use single dash (e.g., `-df`), long flags use double dash (e.g., `--date-from`)
- Functions should have clear docstrings
- Error handling: return None on errors, exit silently in main()
- Use descriptive variable names
- Keep functions focused and small

## Scripts

### slack-list-emojis.py
**Purpose**: Retrieve and count reaction emojis from a Slack channel.

**Environment Variables**:
- `SLACK_TOKEN`: Slack API token (format: `xoxp-...`)

**Arguments**:
- `channel_name` (positional): Slack channel name (with or without `#` prefix)
- `-df, --date-from`: Start date in YYYY-MM-DD format (optional)
- `-dt, --date-to`: End date in YYYY-MM-DD format (optional, includes full day until 23:59:59)

**Output Format**:
```
:emoji_name: - count
```
Sorted ascending by count (most used at the end).

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

# Main checks for None and exits silently
def main():
    result = some_function()
    if result is None:
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
When adding date filters:
- Use YYYY-MM-DD format
- Use `datetime.strptime()` for parsing
- Convert to appropriate format for target API (e.g., Unix timestamp for Slack)
- For end dates, set time to 23:59:59 to include full day
- Exit silently on invalid date format

## Maintenance Notes
- Keep this file updated when adding/modifying scripts
- Update principles if patterns emerge
- Document any non-obvious API quirks or workarounds
- Keep examples current
