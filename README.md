# Markitdown MCP Server Actor

[![Apify](https://img.shields.io/badge/Apify-Actor-blue)](https://apify.com)
[![MCP](https://img.shields.io/badge/MCP-Server-green)](https://modelcontextprotocol.io)

An Apify Actor that provides a Model Context Protocol (MCP) server for [Markitdown](https://github.com/microsoft/markitdown), Microsoft's lightweight Python utility for converting various file formats to Markdown.

## Overview

This Actor wraps the Markitdown MCP server as an Apify Actor, making it easy to deploy and use as a pay-per-event service. Markitdown converts various file formats to Markdown, making them suitable for use with Large Language Models (LLMs) and text analysis pipelines.

### Supported File Formats

- **Documents**: PDF, PowerPoint, Word, Excel
- **Media**: Images (with EXIF metadata and OCR), Audio (with transcription)
- **Web Content**: HTML, YouTube URLs
- **Data Formats**: CSV, JSON, XML
- **Archives**: ZIP files, EPubs

## Features

- **MCP Protocol**: Implements the Model Context Protocol for seamless integration with MCP clients
- **Streamable HTTP Transport**: Uses modern Streamable HTTP transport for efficient communication
- **Pay-per-Event**: Charges only for actual tool usage via Apify's pay-per-event system
- **Session Management**: Automatic session timeout and cleanup after inactivity
- **Standby Mode**: Runs in Apify's standby mode for instant availability

## How It Works

The Actor runs a proxy server that:
1. Connects to the Markitdown MCP server via STDIO transport
2. Exposes a Streamable HTTP endpoint at `/mcp`
3. Forwards MCP requests/responses between clients and the Markitdown server
4. Charges for tool usage via Apify's pay-per-event system

## Available Tools

### `convert_to_markdown`

Converts various file formats to Markdown.

**Parameters:**
- `uri` (string): The URI of the file to convert. Supports:
  - `http://` and `https://` - Remote files
  - `file://` - Local files
  - `data:` - Data URIs

**Example:**
```json
{
  "uri": "https://example.com/document.pdf"
}
```

## Usage

### 1. Deploy the Actor

Deploy this Actor to Apify or run it locally in standby mode.

### 2. Configure Your MCP Client

Add the following configuration to your MCP client (e.g., VS Code, Claude Desktop):

```json
{
  "mcpServers": {
    "markitdown-mcp-server": {
      "type": "http",
      "url": "https://YOUR_ACTOR_URL/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_APIFY_TOKEN"
      }
    }
  }
}
```

### 3. Use the Tool

Once configured, you can use the `convert_to_markdown` tool in your MCP client:

```
Convert this PDF to markdown: https://example.com/document.pdf
```

## Environment Variables

- `SESSION_TIMEOUT_SECS` (default: 300): Session timeout in seconds before terminating idle sessions

## Pricing

The Actor uses Apify's pay-per-event system with the following rates (configurable in `.actor/pay_per_event.json`):

- **CONVERT_TO_MARKDOWN**: $0.01 per conversion
- **TOOL_LIST**: $0.0001 per listing
- **RESOURCE_LIST**: $0.0001 per listing
- **RESOURCE_READ**: $0.001 per read
- **PROMPT_LIST**: $0.0001 per listing
- **PROMPT_GET**: $0.001 per get

## Local Development

### Prerequisites

- Python 3.10 or higher
- Poetry for dependency management
- Docker (optional, for containerized development)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Yash-Kavaiya/Markitdown-MCP-actor.git
cd Markitdown-MCP-actor
```

2. Install dependencies:
```bash
poetry install
```

3. Run the Actor locally:
```bash
poetry run python -m src
```

### Running in Standby Mode

To run the Actor in standby mode (required for MCP server operation):

```bash
export APIFY_META_ORIGIN=STANDBY
export ACTOR_STANDBY_URL=http://localhost:5001
poetry run python -m src
```

The MCP endpoint will be available at: `http://localhost:5001/mcp`

## Project Structure

```
Markitdown-MCP-actor/
├── .actor/                 # Apify Actor configuration
│   ├── actor.json          # Actor metadata and settings
│   ├── pay_per_event.json  # Pricing configuration
│   ├── Dockerfile          # Docker image definition
│   └── .actorignore        # Files to exclude from build
├── src/                    # Source code
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # Main entry point
│   ├── const.py            # Constants and configuration
│   ├── models.py           # Data models
│   ├── server.py           # ProxyServer implementation
│   ├── mcp_gateway.py      # MCP gateway logic
│   └── event_store.py      # Event store for session management
├── pyproject.toml          # Python dependencies and settings
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Customization

### Charging Strategy

You can customize the charging strategy by editing `.actor/pay_per_event.json`. The default configuration charges:
- $0.01 per conversion (main operation)
- Minimal charges for metadata operations (listing tools, resources, prompts)

### Session Timeout

Adjust the `SESSION_TIMEOUT_SECS` environment variable to control how long sessions remain active during inactivity. The default is 300 seconds (5 minutes).

### Tool Whitelist

The Actor uses a tool whitelist defined in `src/const.py`:

```python
TOOL_WHITELIST = {
    'convert_to_markdown': ('CONVERT_TO_MARKDOWN', 1),
}
```

You can add more tools if the underlying Markitdown MCP server exposes them.

## Architecture

The Actor implements a proxy architecture:

```
MCP Client (VS Code, Claude, etc.)
    ↓ (Streamable HTTP)
Proxy Server (This Actor)
    ↓ (STDIO)
Markitdown MCP Server
    ↓
Markitdown Library
```

Key components:
- **ProxyServer**: Manages HTTP server and session lifecycle
- **MCP Gateway**: Proxies MCP requests and handles charging
- **Event Store**: Maintains session history for resumability
- **Session Manager**: Handles Streamable HTTP transport

## Related Links

- [Markitdown GitHub](https://github.com/microsoft/markitdown)
- [Markitdown MCP PyPI](https://pypi.org/project/markitdown-mcp/)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Apify Platform](https://apify.com)
- [Apify MCP Documentation](https://mcp.apify.com/)

## License

Apache-2.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/Yash-Kavaiya/Markitdown-MCP-actor/issues)
- Contact via [Apify Console](https://console.apify.com)

## Acknowledgments

- [Microsoft Markitdown](https://github.com/microsoft/markitdown) - The underlying conversion tool
- [Apify](https://apify.com) - Actor platform and infrastructure
- [MCP Proxy](https://github.com/sparfenyuk/mcp-proxy) - Inspiration for the proxy implementation
