"""Constants for Markitdown MCP Server Actor."""

# Session timeout in seconds (default: 5 minutes)
SESSION_TIMEOUT_SECS = 300

# Tool whitelist for charging
# Format: {tool_name: (event_name, default_count)}
# The convert_to_markdown tool is the main tool provided by Markitdown MCP
TOOL_WHITELIST = {
    'convert_to_markdown': ('CONVERT_TO_MARKDOWN', 1),
}
