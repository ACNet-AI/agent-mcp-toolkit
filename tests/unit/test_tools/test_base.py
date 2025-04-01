"""MCP Base Tool Test Module"""


from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from langchain_mcp_toolkit.tools.base import MCPBaseTool


# Create a test tool subclass
class TestTool(MCPBaseTool):
    """Test Tool Class"""

    name: str = "test_tool"
    description: str = "Test tool description"

    async def _run(self, *args: Any, **kwargs: Any) -> str:
        """Implement _run method"""
        return "Test result"


class TestMCPBaseTool:
    """Test MCPBaseTool class"""

    def test_initialization(self) -> None:
        """Test initialization"""
        tool = MCPBaseTool()
        assert tool.name == ""
        assert tool.description == ""

    @pytest.mark.asyncio
    async def test_run(self) -> None:
        """Test run method"""
        tool = MCPBaseTool()
        with pytest.raises(NotImplementedError, match="Subclasses must implement the _run method"):
            await tool._run({})

    @pytest.mark.asyncio
    async def test_run_implementation(self) -> None:
        """Test _run method implementation"""
        tool = TestTool()

        result = await tool._run(test_arg="value")
        assert result == "Test result"

    @pytest.mark.asyncio
    async def test_arun_calls_run(self) -> None:
        """Test _arun method calls _run method"""
        tool = TestTool()

        # Use patch instead of setattr
        with patch.object(tool, '_run', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = "Mock result"

            result = await tool._arun(test_arg="value")
            assert result == "Mock result"
            mock_run.assert_called_once_with(test_arg="value")

    @pytest.mark.asyncio
    async def test_unimplemented_run(self) -> None:
        """Test unimplemented _run method"""
        # Create a base class instance without implementing _run
        base_tool = MCPBaseTool()
        base_tool.name = "base_tool"
        base_tool.description = "Base tool"

        with pytest.raises(NotImplementedError, match="Subclasses must implement the _run method"):
            await base_tool._run()
