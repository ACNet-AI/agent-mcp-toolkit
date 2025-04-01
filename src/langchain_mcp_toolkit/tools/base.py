"""
MCP Base Tool Module

This module defines the base class for MCP tools, all specific MCP tools inherit from this base class.
MCPBaseTool inherits from LangChain's BaseTool, providing integration capabilities with LangChain.

Main contents:
- MCPBaseTool: Base class for MCP tools, parent class for all specific tools
"""

from typing import Any

from langchain.tools import BaseTool


class MCPBaseTool(BaseTool):
    """
    MCP Base Tool Class

    Base class for all MCP tools, inherits from LangChain's BaseTool, providing unified interface and behavior.
    Subclasses need to implement the _run method to provide specific functionality. This class runs asynchronously by default,
    the _arun method will automatically call the _run method.

    Attributes:
        name: Tool name
        description: Tool description

    Example:
        ```python
        # Define a simple MCP tool
        class MyMCPTool(MCPBaseTool):
            name = "my_tool"
            description = "This is an example tool"

            async def _run(self, query: str) -> str:
                return f"Processing query: {query}"

        # Use the tool
        my_tool = MyMCPTool()
        result = await my_tool.invoke({"query": "Test query"})
        print(result)  # Output: Processing query: Test query
        ```
    """

    name: str = ""
    description: str = ""

    async def _run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Abstract method to run the tool, must be overridden by subclasses

        This is the core method of the tool, all subclasses must implement this method to provide specific functionality.

        Parameters:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Any: Result of the tool execution

        Exceptions:
            NotImplementedError: If the subclass does not implement this method

        Example:
            ```python
            # Implement _run method in subclass
            async def _run(self, text: str) -> str:
                # Process input and return result
                return f"Tool processing result: {text.upper()}"
            ```
        """
        raise NotImplementedError("Subclasses must implement the _run method")

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        """
        Method to run the tool asynchronously

        This method is already implemented and will automatically call the _run method. Usually, you don't need to override this method in subclasses.

        Parameters:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Any: Result of the tool execution

        Example:
            ```python
            # Usually no need to override this method
            # Will be used automatically when calling the tool
            result = await tool.arun(text="hello")
            ```
        """
        return await self._run(*args, **kwargs)
