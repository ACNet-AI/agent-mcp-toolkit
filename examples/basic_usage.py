# type: ignore
"""Basic Usage Example

This example demonstrates how to use agent-mcp-toolkit to create servers, clients, register and call tools.
"""

import asyncio
import os
from typing import Any

from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage
from langgraph.prebuilt import create_react_agent

from langchain_mcp_toolkit import MCPToolkit


async def basic_demo() -> None:
    """Basic functionality demonstration"""
    # Set API key (in actual use, get from environment variables or configuration file)
    os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

    print("Creating MCP toolkit...")
    # Create full-featured toolkit (includes server and client tools)
    toolkit = MCPToolkit(mode="client_and_server")

    # Get all tools
    tools = toolkit.get_tools()
    print(f"Loaded {len(tools)} tools")

    # Create Agent
    model = ChatOpenAI(model="gpt-3.5-turbo")
    agent: Any = create_react_agent(model, tools)

    # Prompt content
    prompt = """
    Please perform the following tasks:
    1. Start an MCP server
    2. Add a tool named "hello" that returns "Hello, World!"
    3. List the tools on the server
    4. Call the "hello" tool
    5. Stop the server
    """

    print("Running Agent...")
    messages: list[HumanMessage | AIMessage] = [HumanMessage(content=prompt)]
    response = await agent.ainvoke({"messages": messages})

    # Print results
    print("\nFinal results:")
    if response and "messages" in response:
        for message in response["messages"]:
            if message["role"] == "assistant":
                print(message["content"])


async def server_only_demo() -> None:
    """Server-only functionality demonstration"""
    # Create server-only toolkit
    toolkit = MCPToolkit(mode="server")

    # Get server tools
    server_tools = toolkit.get_tools()
    print(f"Number of server tools: {len(server_tools)}")

    # List tool names
    for tool in server_tools:
        print(f" - {tool.name}: {tool.description[:50]}...")


async def client_only_demo() -> None:
    """Client-only functionality demonstration"""
    # Create client-only toolkit
    toolkit = MCPToolkit(mode="client")

    # Get client tools
    client_tools = toolkit.get_tools()
    print(f"Number of client tools: {len(client_tools)}")

    # List tool names
    for tool in client_tools:
        print(f" - {tool.name}: {tool.description[:50]}...")


if __name__ == "__main__":
    print("Agent MCP Toolkit Examples\n")

    print("=" * 50)
    print("Example 1: Server Tools")
    print("=" * 50)
    asyncio.run(server_only_demo())

    print("\n" + "=" * 50)
    print("Example 2: Client Tools")
    print("=" * 50)
    asyncio.run(client_only_demo())

    # Complete example requires a valid API key, uncomment to run
    # print("\n" + "=" * 50)
    # print("Example 3: Full Agent Functionality")
    # print("=" * 50)
    # asyncio.run(basic_demo())
