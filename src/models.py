"""Data models for MCP Server Actor."""

from enum import Enum

from mcp.client.stdio import StdioServerParameters
from pydantic import BaseModel


class ServerType(str, Enum):
    """Type of MCP server to connect to."""

    STDIO = 'stdio'
    SSE = 'sse'
    HTTP = 'http'


class RemoteServerParameters(BaseModel):
    """Parameters for connecting to a remote MCP server (SSE or HTTP)."""

    url: str
    headers: dict[str, str] | None = None


# Union type for server parameters
ServerParameters = StdioServerParameters | RemoteServerParameters
