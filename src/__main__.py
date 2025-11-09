"""Main entry point for the Markitdown MCP Server Actor."""

import os

from apify import Actor

from .const import SESSION_TIMEOUT_SECS, TOOL_WHITELIST
from .models import ServerType
from .server import ProxyServer

# Actor configuration
STANDBY_MODE = os.environ.get('APIFY_META_ORIGIN') == 'STANDBY'
# Bind to all interfaces (0.0.0.0) as this is running in a containerized environment (Apify Actor)
# The container's network is isolated, so this is safe
HOST = '0.0.0.0'  # noqa: S104 - Required for container networking at Apify platform
PORT = (Actor.is_at_home() and int(os.environ.get('ACTOR_STANDBY_PORT') or '5001')) or 5001
SERVER_NAME = 'markitdown-mcp-server'  # Name of the MCP server, without spaces

# MARKITDOWN MCP CONFIGURATION -------------------------------------------------
# Configuration for the Markitdown MCP server
# Markitdown is a Python tool that converts various file formats (PDF, Word, Excel,
# PowerPoint, Images, Audio, etc.) to Markdown for use with LLMs and text analysis.
from mcp.client.stdio import StdioServerParameters  # noqa: E402

server_type = ServerType.STDIO
MCP_SERVER_PARAMS = StdioServerParameters(
    command='uvx',
    args=['markitdown-mcp'],
    env=None,  # No special environment variables needed for Markitdown
)

# Alternative: If you have markitdown-mcp installed globally or in the environment
# MCP_SERVER_PARAMS = StdioServerParameters(
#     command='markitdown-mcp',
#     args=[],
#     env=None,
# )
# ------------------------------------------------------------------------------

session_timeout_secs = int(os.getenv('SESSION_TIMEOUT_SECS', SESSION_TIMEOUT_SECS))


async def main() -> None:
    """Run the Markitdown MCP Server Actor.

    This Actor provides a proxy to the Markitdown MCP server, which converts
    various file formats to Markdown. The server exposes the convert_to_markdown
    tool that accepts URIs with http:, https:, file:, or data: schemes.

    CHARGING STRATEGY:
    The Actor charges for the convert_to_markdown tool call at a flat rate.
    You can customize the charging amount in .actor/pay_per_event.json

    SUPPORTED FORMATS:
    - Documents: PDF, Word, Excel, PowerPoint
    - Media: Images (with EXIF/OCR), Audio (with transcription)
    - Web: HTML, YouTube URLs
    - Data: CSV, JSON, XML
    - Archives: ZIP files, EPubs
    """
    async with Actor:
        url = os.environ.get('ACTOR_STANDBY_URL', HOST)
        if not STANDBY_MODE:
            msg = (
                'Actor is not designed to run in the NORMAL mode. Use MCP server URL to connect to the server.\n'
                f'Connect to {url}/mcp to establish a connection.\n'
                'Learn more at https://mcp.apify.com/'
            )
            Actor.log.info(msg)
            await Actor.exit(status_message=msg)
            return

        try:
            # Create and start the server with charging enabled
            Actor.log.info('Starting Markitdown MCP server')
            Actor.log.info('Add the following configuration to your MCP client to use Streamable HTTP transport:')
            Actor.log.info(
                f"""
                {{
                    "mcpServers": {{
                        "{SERVER_NAME}": {{
                            "url": "{url}/mcp",
                        }}
                    }}
                }}
                """
            )
            # Pass Actor.charge to enable charging for MCP operations
            # The proxy server will use this to charge for convert_to_markdown tool calls
            proxy_server = ProxyServer(
                SERVER_NAME,
                MCP_SERVER_PARAMS,
                HOST,
                PORT,
                server_type,
                actor_charge_function=Actor.charge,
                tool_whitelist=TOOL_WHITELIST,
                session_timeout_secs=session_timeout_secs,
            )
            await proxy_server.start()
        except Exception as e:
            Actor.log.exception(f'Server failed to start: {e}')
            await Actor.exit()
            raise
