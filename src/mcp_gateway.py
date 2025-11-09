"""MCP Gateway for proxying and charging."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from mcp import types
from mcp.server import Server

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Sequence

    from mcp.client.session import ClientSession

logger = logging.getLogger('apify')


async def create_gateway(
    session: ClientSession,
    actor_charge_function: Callable[[str, int], Awaitable[Any]] | None = None,
    tool_whitelist: dict[str, tuple[str, int]] | None = None,
) -> Server:
    """Create an MCP gateway server that proxies requests to a backend session.

    Args:
        session: The MCP client session to proxy to
        actor_charge_function: Optional function to charge for operations
        tool_whitelist: Optional dict mapping tool names to (event_name, default_count)

    Returns:
        An MCP Server instance configured as a gateway
    """
    server = Server('markitdown-mcp-gateway')

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        """List available tools from the backend server."""
        result = await session.list_tools()
        tools = result.tools

        # Filter tools if whitelist is provided
        if tool_whitelist:
            tools = [tool for tool in tools if tool.name in tool_whitelist]

        # Charge for tool listing if charging is enabled
        if actor_charge_function:
            await actor_charge_function('TOOL_LIST', 1)

        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Call a tool on the backend server.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool execution results
        """
        # Check whitelist if enabled
        if tool_whitelist and name not in tool_whitelist:
            raise ValueError(f'Tool {name} is not whitelisted')

        # Charge for tool call if charging is enabled
        if actor_charge_function and tool_whitelist and name in tool_whitelist:
            event_name, default_count = tool_whitelist[name]
            await actor_charge_function(event_name, default_count)

        # Execute the tool call
        result = await session.call_tool(name, arguments)
        return result.content

    @server.list_resources()
    async def list_resources() -> list[types.Resource]:
        """List available resources from the backend server."""
        result = await session.list_resources()

        # Charge for resource listing if charging is enabled
        if actor_charge_function:
            await actor_charge_function('RESOURCE_LIST', 1)

        return result.resources

    @server.read_resource()
    async def read_resource(uri: str) -> str | bytes:
        """Read a resource from the backend server.

        Args:
            uri: Resource URI

        Returns:
            Resource contents
        """
        # Charge for resource read if charging is enabled
        if actor_charge_function:
            await actor_charge_function('RESOURCE_READ', 1)

        result = await session.read_resource(uri)
        # Combine all text/blob contents
        contents = []
        for content in result.contents:
            if isinstance(content, types.TextContent):
                contents.append(content.text)
            elif isinstance(content, types.BlobContent):
                contents.append(content.blob)

        return ''.join(str(c) for c in contents)

    @server.list_prompts()
    async def list_prompts() -> list[types.Prompt]:
        """List available prompts from the backend server."""
        result = await session.list_prompts()

        # Charge for prompt listing if charging is enabled
        if actor_charge_function:
            await actor_charge_function('PROMPT_LIST', 1)

        return result.prompts

    @server.get_prompt()
    async def get_prompt(
        name: str, arguments: dict[str, str] | None = None
    ) -> types.GetPromptResult:
        """Get a prompt from the backend server.

        Args:
            name: Prompt name
            arguments: Optional prompt arguments

        Returns:
            Prompt result
        """
        # Charge for prompt get if charging is enabled
        if actor_charge_function:
            await actor_charge_function('PROMPT_GET', 1)

        return await session.get_prompt(name, arguments)

    return server
