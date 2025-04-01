"""Global Test Fixtures Configuration"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from langchain_mcp_toolkit.services.client_service import MCPClientService
from langchain_mcp_toolkit.services.server_service import MCPServerService

# Add project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_client_service() -> MCPClientService:
    """Create mock client service"""
    # Base mock object uses MagicMock, synchronous methods also use MagicMock
    mock = MagicMock(spec=MCPClientService)

    # Set return values for synchronous methods
    mock.create.return_value = "Client created"
    mock.is_connected = True

    # Set up asynchronous methods
    mock.connect = AsyncMock()
    mock.disconnect = AsyncMock()
    mock.call_tool = AsyncMock(return_value={"result": "Tool call result"})
    mock.list_tools = AsyncMock(return_value=["tool1", "tool2"])
    mock.list_resources = AsyncMock(return_value=["resource1", "resource2"])
    mock.read_resource = AsyncMock(return_value={"content": "Resource content"})
    mock.list_prompts = AsyncMock(return_value=["prompt1", "prompt2"])
    mock.get_prompt = AsyncMock(return_value="Prompt content")
    mock.get_langchain_tools = AsyncMock(return_value=["langchain_tool1", "langchain_tool2"])
    mock.get_langchain_prompt = AsyncMock(return_value={"template": "Prompt template"})

    return mock


@pytest.fixture
def mock_server_service() -> MCPServerService:
    """Create mock server service"""
    mock = AsyncMock(spec=MCPServerService)

    # Set return values for various methods
    mock.create_default_server.return_value = "Default server created"
    mock.start_server.return_value = "Server started"
    mock.stop_server.return_value = "Server stopped"
    mock.get_url.return_value = "http://localhost:8000"
    mock.add_tool.return_value = "Tool added"
    mock.add_resource.return_value = "Resource added"
    mock.add_prompt.return_value = "Prompt added"

    # Set return values for asynchronous methods
    mock.async_start_server.return_value = "Server started"
    mock.async_stop_server.return_value = "Server stopped"
    mock.async_get_url.return_value = "http://localhost:8000"
    mock.async_add_tool.return_value = "Tool added"
    mock.async_add_resource.return_value = "Resource added"
    mock.async_add_prompt.return_value = "Prompt added"

    return mock
