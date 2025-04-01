"""Adapter Service Test Module"""

from unittest.mock import MagicMock, patch

import pytest
from langchain.tools import BaseTool
from langchain_core.messages import AIMessage, HumanMessage
from mcp.types import PromptMessage, Tool

from langchain_mcp_toolkit.services.adapters import MCPAdapterService


class TestMCPAdapterService:
    """Test MCPAdapterService class"""

    def test_initialization(self) -> None:
        """Test initialization"""
        service = MCPAdapterService()
        assert service is not None

    @pytest.mark.asyncio
    async def test_create_multi_server_client(self) -> None:
        """Test creating multi-server client"""
        servers = {
            "server1": {"url": "http://localhost:8001", "transport_type": "sse"},
            "server2": {"url": "http://localhost:8002", "transport_type": "stdio"},
        }
        client = await MCPAdapterService.create_multi_server_client(servers)
        assert client is not None

    @pytest.mark.asyncio
    async def test_load_tools_from_session(self) -> None:
        """Test loading tools from session"""
        mock_session = MagicMock()
        # Mock load_mcp_tools behavior
        with patch("langchain_mcp_toolkit.services.adapters.load_mcp_tools") as mock_load_tools:
            mock_tool = MagicMock(spec=BaseTool)
            mock_load_tools.return_value = [mock_tool]

            tools = await MCPAdapterService.load_tools_from_session(mock_session)

            assert len(tools) == 1
            assert tools[0] == mock_tool
            mock_load_tools.assert_called_once_with(mock_session)

    @pytest.mark.asyncio
    async def test_load_tools_from_session_empty(self) -> None:
        """Test loading tools from empty session"""
        mock_session = MagicMock()
        # Mock load_mcp_tools behavior
        with patch("langchain_mcp_toolkit.services.adapters.load_mcp_tools") as mock_load_tools:
            mock_load_tools.return_value = []

            tools = await MCPAdapterService.load_tools_from_session(mock_session)

            assert len(tools) == 0
            mock_load_tools.assert_called_once_with(mock_session)

    @pytest.mark.asyncio
    async def test_load_tools_from_session_error(self) -> None:
        """Test error when loading tools from session"""
        mock_session = MagicMock()
        # Mock load_mcp_tools throwing exception
        with patch("langchain_mcp_toolkit.services.adapters.load_mcp_tools") as mock_load_tools:
            mock_load_tools.side_effect = Exception("Failed to load tools")

            with pytest.raises(Exception, match="Failed to load tools"):
                await MCPAdapterService.load_tools_from_session(mock_session)

            mock_load_tools.assert_called_once_with(mock_session)

    def test_convert_tool_to_langchain(self) -> None:
        """Test converting MCP tool to LangChain tool"""
        with patch(
            "langchain_mcp_toolkit.services.adapters.convert_mcp_tool_to_langchain_tool"
        ) as mock_convert:
            mock_tool = MagicMock(spec=BaseTool)
            mock_convert.return_value = mock_tool

            mcp_tool = MagicMock(spec=Tool)
            result = MCPAdapterService.convert_tool_to_langchain(mcp_tool)

            mock_convert.assert_called_once_with(mcp_tool)
            assert result == mock_tool

    def test_convert_prompt_to_langchain(self) -> None:
        """Test converting MCP prompt to LangChain message"""
        with patch(
            "langchain_mcp_toolkit.services.adapters.convert_mcp_prompt_message_to_langchain_message"
        ) as mock_convert:
            mock_message = MagicMock(spec=HumanMessage)
            mock_convert.return_value = mock_message

            mcp_message = MagicMock(spec=PromptMessage)
            result = MCPAdapterService.convert_prompt_to_langchain(mcp_message)

            mock_convert.assert_called_once_with(mcp_message)
            assert result == mock_message

    @pytest.mark.asyncio
    async def test_load_prompt_from_session(self) -> None:
        """Test loading LangChain prompt messages from session"""
        with patch("langchain_mcp_toolkit.services.adapters.load_mcp_prompt") as mock_load:
            mock_messages = [MagicMock(spec=HumanMessage), MagicMock(spec=AIMessage)]
            mock_load.return_value = mock_messages

            mock_session = MagicMock()
            prompt_name = "test_prompt"
            arguments = {"key": "value"}

            result = await MCPAdapterService.load_prompt_from_session(
                mock_session, prompt_name, arguments
            )

            mock_load.assert_called_once_with(mock_session, prompt_name, arguments)
            assert result == mock_messages

    @pytest.mark.asyncio
    async def test_load_prompt_from_session_no_arguments(self) -> None:
        """Test loading LangChain prompt messages from session without arguments"""
        with patch("langchain_mcp_toolkit.services.adapters.load_mcp_prompt") as mock_load:
            mock_messages = [MagicMock(spec=HumanMessage)]
            mock_load.return_value = mock_messages

            mock_session = MagicMock()
            prompt_name = "test_prompt"

            result = await MCPAdapterService.load_prompt_from_session(
                mock_session, prompt_name
            )

            mock_load.assert_called_once_with(mock_session, prompt_name, None)
            assert result == mock_messages
