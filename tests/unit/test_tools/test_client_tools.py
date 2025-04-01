"""Client Tools Unit Tests"""


import pytest

from langchain_mcp_toolkit.services.client_service import MCPClientService
from langchain_mcp_toolkit.tools.client_tools import (
    ClientCallToolTool,
    ClientCreateTool,
    ClientGetPromptTool,
    ClientListPromptsTool,
    ClientListResourcesTool,
    ClientListToolsTool,
    ClientReadResourceTool,
    GetLangChainPromptTool,
    GetLangChainToolsTool,
)


class TestClientCreateTool:
    """Test ClientCreateTool class"""

    def test_initialization(self, mock_client_service: MCPClientService) -> None:
        """Test tool initialization"""
        tool = ClientCreateTool(client_service=mock_client_service)
        assert tool.name == "client_create"
        assert tool.description is not None
        assert tool.client_service == mock_client_service

    @pytest.mark.asyncio
    async def test_run(self, mock_client_service: MCPClientService) -> None:
        """Test running tool"""
        # Prepare test return value
        mock_client_service.create.return_value = "Client created"

        tool = ClientCreateTool(client_service=mock_client_service)
        # Use await, because _run is an asynchronous method
        # Note: the default value of transport_type is "stdio", so if not specified, it will use this default value
        result = await tool._run("http://localhost:8000", transport_type="sse")
        assert result == "Client created"
        mock_client_service.create.assert_called_once_with("http://localhost:8000", "sse")


class TestClientCallToolTool:
    """Test ClientCallToolTool class"""

    def test_initialization(self, mock_client_service: MCPClientService) -> None:
        """Test tool initialization"""
        tool = ClientCallToolTool(client_service=mock_client_service)
        assert tool.name == "client_call_tool"
        assert tool.description is not None
        assert tool.client_service == mock_client_service

    @pytest.mark.asyncio
    async def test_run(self, mock_client_service: MCPClientService) -> None:
        """Test running tool"""
        tool = ClientCallToolTool(client_service=mock_client_service)
        server_name = "default"
        tool_name = "test_tool"
        arguments = {"param": "value"}
        result = await tool._run(server_name, tool_name, arguments)
        assert result == {"result": "Tool call result"}
        mock_client_service.call_tool.assert_called_once_with(server_name, tool_name, **arguments)


class TestClientListToolsTool:
    """Test ClientListToolsTool class"""

    def test_initialization(self, mock_client_service: MCPClientService) -> None:
        """Test tool initialization"""
        tool = ClientListToolsTool(client_service=mock_client_service)
        assert tool.name == "client_list_tools"
        assert tool.description is not None
        assert tool.client_service == mock_client_service

    @pytest.mark.asyncio
    async def test_run(self, mock_client_service: MCPClientService) -> None:
        """Test running tool"""
        tool = ClientListToolsTool(client_service=mock_client_service)
        include_server_prefix = True
        result = await tool._run(include_server_prefix)
        assert result == ["tool1", "tool2"]
        mock_client_service.list_tools.assert_called_once_with(include_server_prefix=include_server_prefix)


class TestClientListResourcesTool:
    """Test ClientListResourcesTool class"""

    def test_initialization(self, mock_client_service: MCPClientService) -> None:
        """Test tool initialization"""
        tool = ClientListResourcesTool(client_service=mock_client_service)
        assert tool.name == "client_list_resources"
        assert tool.description is not None
        assert tool.client_service == mock_client_service

    @pytest.mark.asyncio
    async def test_run(self, mock_client_service: MCPClientService) -> None:
        """Test running tool"""
        tool = ClientListResourcesTool(client_service=mock_client_service)
        server_name = "default"
        # Adjust according to the actual parameter order in the source code
        result = await tool._run(resource_type="collection", server_name=server_name)
        assert result == ["resource1", "resource2"]
        mock_client_service.list_resources.assert_called_once_with(server_name)


class TestClientReadResourceTool:
    """Test ClientReadResourceTool class"""

    def test_initialization(self, mock_client_service: MCPClientService) -> None:
        """Test tool initialization"""
        tool = ClientReadResourceTool(client_service=mock_client_service)
        assert tool.name == "client_read_resource"
        assert tool.description is not None
        assert tool.client_service == mock_client_service

    @pytest.mark.asyncio
    async def test_run(self, mock_client_service: MCPClientService) -> None:
        """Test running tool"""
        tool = ClientReadResourceTool(client_service=mock_client_service)
        server_name = "default"
        resource_name = "resource1"
        # Adjust according to the actual parameter order in the source code
        result = await tool._run(resource_name, server_name)
        assert result == {"content": "Resource content"}
        mock_client_service.read_resource.assert_called_once_with(server_name, resource_name)


class TestClientListPromptsTool:
    """Test ClientListPromptsTool class"""

    def test_initialization(self, mock_client_service: MCPClientService) -> None:
        """Test tool initialization"""
        tool = ClientListPromptsTool(client_service=mock_client_service)
        assert tool.name == "client_list_prompts"
        assert tool.description is not None
        assert tool.client_service == mock_client_service

    @pytest.mark.asyncio
    async def test_run(self, mock_client_service: MCPClientService) -> None:
        """Test running tool"""
        tool = ClientListPromptsTool(client_service=mock_client_service)
        server_name = "default"
        result = await tool._run(server_name)
        assert result == ["prompt1", "prompt2"]
        mock_client_service.list_prompts.assert_called_once_with(server_name)


class TestClientGetPromptTool:
    """Test ClientGetPromptTool class"""

    def test_initialization(self, mock_client_service: MCPClientService) -> None:
        """Test tool initialization"""
        tool = ClientGetPromptTool(client_service=mock_client_service)
        assert tool.name == "client_get_prompt"
        assert tool.description is not None
        assert tool.client_service == mock_client_service

    @pytest.mark.asyncio
    async def test_run(self, mock_client_service: MCPClientService) -> None:
        """Test running tool"""
        tool = ClientGetPromptTool(client_service=mock_client_service)
        server_name = "default"
        prompt_name = "test_prompt"
        result = await tool._run(server_name, prompt_name)
        assert result == "Prompt content"
        mock_client_service.get_prompt.assert_called_once_with(prompt_name, {}, server_name)


class TestGetLangChainToolsTool:
    """Test GetLangChainToolsTool class"""

    def test_initialization(self, mock_client_service: MCPClientService) -> None:
        """Test tool initialization"""
        tool = GetLangChainToolsTool(client_service=mock_client_service)
        assert tool.name == "get_langchain_tools"
        assert tool.description is not None
        assert tool.client_service == mock_client_service

    @pytest.mark.asyncio
    async def test_run(self, mock_client_service: MCPClientService) -> None:
        """Test running tool"""
        tool = GetLangChainToolsTool(client_service=mock_client_service)
        result = await tool._run()
        assert result == ["langchain_tool1", "langchain_tool2"]
        mock_client_service.get_langchain_tools.assert_called_once()


class TestGetLangChainPromptTool:
    """Test GetLangChainPromptTool class"""

    def test_initialization(self, mock_client_service: MCPClientService) -> None:
        """Test tool initialization"""
        tool = GetLangChainPromptTool(client_service=mock_client_service)
        assert tool.name == "get_langchain_prompt"
        assert tool.description is not None
        assert tool.client_service == mock_client_service

    @pytest.mark.asyncio
    async def test_run(self, mock_client_service: MCPClientService) -> None:
        """Test running tool"""
        tool = GetLangChainPromptTool(client_service=mock_client_service)
        server_name = "default"
        prompt_name = "test_prompt"
        arguments = {"var1": "value1"}
        result = await tool._run(server_name, prompt_name, arguments)
        assert result == {"template": "Prompt template"}
        mock_client_service.get_langchain_prompt.assert_called_once_with(
            prompt_name, arguments, server_name
        )
