"""MCP Adapter Service Module"""

from typing import Any, Protocol, cast

from langchain.tools import BaseTool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient  # type: ignore
from langchain_mcp_adapters.prompts import (  # type: ignore
    convert_mcp_prompt_message_to_langchain_message,
    load_mcp_prompt,
)
from langchain_mcp_adapters.tools import (  # type: ignore
    convert_mcp_tool_to_langchain_tool,
    load_mcp_tools,
)
from mcp.types import PromptMessage, Tool  # type: ignore


# Define session protocol
class SessionProtocol(Protocol):
    """Session protocol, used for type checking"""

    async def get_prompt(self, name: str, arguments: dict[str, Any]) -> Any:
        """Get prompt"""
        ...

    async def get_tools(self) -> list[Any]:
        """Get tools"""
        ...

class MCPAdapterService:
    """MCP Adapter Service Class"""

    @staticmethod
    async def create_multi_server_client(
        server_configs: dict[str, dict[str, Any]],
    ) -> MultiServerMCPClient:
        """Create multi-server MCP client

        Args:
            server_configs: Server configuration dictionary, in the format of {
                "server_name": {
                    "url": "http://localhost:8000/sse",  # SSE connection
                    "transport": "sse"
                },
                "server_name2": {
                    "command": "python",  # STDIO connection
                    "args": ["path/to/server.py"],
                    "transport": "stdio"
                }
            }

        Returns:
            MultiServerMCPClient: Multi-server client instance
        """
        return MultiServerMCPClient(server_configs)

    @staticmethod
    def create_multi_server_client_sync(
        server_configs: dict[str, dict[str, Any]],
    ) -> MultiServerMCPClient:
        """Create multi-server MCP client (synchronous version)

        Same functionality as the asynchronous version create_multi_server_client,
        but provides a synchronous interface to avoid issues with asyncio.run()
        in test environments.

        Args:
            server_configs: Server configuration dictionary, in the format of {
                "server_name": {
                    "url": "http://localhost:8000/sse",  # SSE connection
                    "transport": "sse"
                },
                "server_name2": {
                    "command": "python",  # STDIO connection
                    "args": ["path/to/server.py"],
                    "transport": "stdio"
                }
            }

        Returns:
            MultiServerMCPClient: Multi-server client instance
        """
        return MultiServerMCPClient(server_configs)

    @staticmethod
    def convert_tool_to_langchain(tool: Tool) -> BaseTool:
        """Convert MCP tool to LangChain tool

        Args:
            tool: MCP tool instance

        Returns:
            BaseTool: LangChain tool instance
        """
        return cast(BaseTool, convert_mcp_tool_to_langchain_tool(tool))

    @staticmethod
    def convert_prompt_to_langchain(message: PromptMessage) -> HumanMessage | AIMessage:
        """Convert MCP prompt to LangChain message

        Args:
            message: MCP prompt message

        Returns:
            HumanMessage | AIMessage: LangChain message
        """
        return cast(HumanMessage | AIMessage, convert_mcp_prompt_message_to_langchain_message(message))

    @staticmethod
    async def load_tools_from_session(session: SessionProtocol) -> list[BaseTool]:
        """Load LangChain tools from session

        Args:
            session: MCP session instance

        Returns:
            list[BaseTool]: LangChain tools list
        """
        return cast(list[BaseTool], await load_mcp_tools(session))

    @staticmethod
    async def load_prompt_from_session(
        session: SessionProtocol, name: str, arguments: dict[str, Any] | None = None
    ) -> list[HumanMessage | AIMessage]:
        """Load LangChain prompt messages from session

        Args:
            session: MCP session instance
            name: Prompt name
            arguments: Prompt arguments, optional

        Returns:
            list[HumanMessage | AIMessage]: LangChain message list
        """
        return cast(list[HumanMessage | AIMessage], await load_mcp_prompt(session, name, arguments))
