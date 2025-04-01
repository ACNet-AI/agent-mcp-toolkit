# type: ignore
"""Custom Tools Example

This example demonstrates how to create custom tools and add them to an MCP server.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Any

from langchain.agents import AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage
from langgraph.prebuilt import create_react_agent

from langchain_mcp_toolkit import MCPToolkit


# Define some custom tool functions
def get_current_time(**kwargs: Any) -> str:
    """Return current time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate(**kwargs: Any) -> str:
    """Simple calculator"""
    expression = kwargs.get("expression", "")
    try:
        # Safe execution environment, only supports basic operations
        allowed_chars = set("0123456789+-*/() .")
        if any(c not in allowed_chars for c in expression):
            return "Error: Expression contains disallowed characters"

        result = eval(expression)
        return f"Calculation result: {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"


def search_weather(**kwargs: Any) -> str:
    """Simulated weather search"""
    city = kwargs.get("city", "")
    # Simulated weather data
    weather_data: dict[str, dict[str, str]] = {
        "New York": {"temp": "25°C", "condition": "Sunny"},
        "Los Angeles": {"temp": "28°C", "condition": "Cloudy"},
        "Chicago": {"temp": "32°C", "condition": "Showers"},
        "San Francisco": {"temp": "30°C", "condition": "Thunderstorms"},
    }

    if city in weather_data:
        data = weather_data[city]
        return json.dumps(
            {
                "city": city,
                "temperature": data["temp"],
                "condition": data["condition"],
                "updated_at": get_current_time(),
            },
            ensure_ascii=False,
        )
    else:
        return f"Weather information for {city} not found"


async def custom_tools_demo() -> None:
    """Custom tools demonstration"""
    # Create toolkit
    toolkit = MCPToolkit(mode="server")
    server_service = toolkit.get_server_service()

    # 1. Start server
    print("Starting MCP server...")
    await server_service.async_start_server()
    print(f"Server started: {await server_service.async_get_url()}")

    # 2. Add custom tools
    print("\nAdding custom tools...")

    # 2.1 Add time tool
    time_code = "return datetime.now().strftime('%Y-%m-%d %H:%M:%S')"
    await server_service.add_tool("get_time", "Return current time", time_code)
    print("Added get_time tool")

    # 2.2 Add calculator tool
    calc_code = """
expression = kwargs.get("expression", "")
try:
    # Safe execution environment, only supports basic operations
    allowed_chars = set("0123456789+-*/() .")
    if any(c not in allowed_chars for c in expression):
        return "Error: Expression contains disallowed characters"

    result = eval(expression)
    return f"Calculation result: {result}"
except Exception as e:
    return f"Calculation error: {str(e)}"
"""
    await server_service.add_tool("calculator", "Simple calculator, accepts an expression parameter", calc_code)
    print("Added calculator tool")

    # 2.3 Add weather tool
    weather_code = """
city = kwargs.get("city", "")
# Simulated weather data
weather_data = {
    "New York": {"temp": "25°C", "condition": "Sunny"},
    "Los Angeles": {"temp": "28°C", "condition": "Cloudy"},
    "Chicago": {"temp": "32°C", "condition": "Showers"},
    "San Francisco": {"temp": "30°C", "condition": "Thunderstorms"}
}

if city in weather_data:
    data = weather_data[city]
    return json.dumps({
        "city": city,
        "temperature": data["temp"],
        "condition": data["condition"],
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }, ensure_ascii=False)
else:
    return f"Weather information for {city} not found"
"""
    await server_service.add_tool("weather", "Query city weather, accepts a city parameter", weather_code)
    print("Added weather tool")

    # 3. Create client
    print("\nCreating client connection...")
    client_toolkit = MCPToolkit(mode="client")
    client_service = client_toolkit.get_client_service()

    # Create client connection
    server_url = await server_service.async_get_url()
    await client_service.create("default", {"url": f"{server_url}/sse", "transport": "sse"})

    # List tools on the server
    print("\nGetting server tool list...")
    tools = await client_service.list_tools()
    print(f"Server has {len(tools)} tools:")
    for tool in tools:
        print(f" - {tool['name']}: {tool['description']}")

    # 4. Test tool calls
    print("\nTesting tool calls...")

    # 4.1 Call time tool
    time_result = await client_service.call_tool("get_time")
    print(f"Current time: {time_result}")

    # 4.2 Call calculator tool
    calc_result = await client_service.call_tool("calculator", {"expression": "2 * (3 + 4) - 5"})
    print(f"Calculation result: {calc_result}")

    # 4.3 Call weather tool
    weather_result = await client_service.call_tool("weather", {"city": "New York"})
    print(f"New York weather: {weather_result}")

    # 5. Stop server
    print("\nStopping server...")
    await server_service.async_stop_server()
    print("Server stopped")


async def agent_with_custom_tools() -> None:
    """Agent example with custom tools"""
    # Set API key
    os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

    # Start server and add tools
    toolkit = MCPToolkit(mode="client_and_server")
    server_service = toolkit.get_server_service()

    print("Starting server and adding tools...")
    await server_service.async_start_server()

    # Add weather tool
    weather_code = """
city = kwargs.get("city", "")
# Simulated weather data
weather_data = {
    "New York": {"temp": "25°C", "condition": "Sunny"},
    "Los Angeles": {"temp": "28°C", "condition": "Cloudy"},
    "Chicago": {"temp": "32°C", "condition": "Showers"},
    "San Francisco": {"temp": "30°C", "condition": "Thunderstorms"}
}

if city in weather_data:
    data = weather_data[city]
    return json.dumps({
        "city": city,
        "temperature": data["temp"],
        "condition": data["condition"]
    }, ensure_ascii=False)
else:
    return f"Weather information for {city} not found"
"""
    await server_service.add_tool("weather", "Query city weather, accepts a city parameter", weather_code)

    # Create LangChain Agent
    tools = toolkit.get_tools()
    model = ChatOpenAI(model="gpt-3.5-turbo")
    agent: Any = create_react_agent(model, tools)

    if agent is None:
        print("Unable to create Agent")
        return

    agent_executor: Any = AgentExecutor(agent=agent, tools=tools)

    # Run Agent
    prompt = "Please first connect to the MCP server, then query the weather for New York and Los Angeles, and finally provide a summary comparison."
    messages: list[HumanMessage | AIMessage] = [HumanMessage(content=prompt)]

    print("Running Agent to query weather...")
    try:
        response = await agent_executor.ainvoke({"messages": messages})

        # Print results
        print("\nFinal results:")
        if response and "messages" in response:
            for message in response["messages"]:
                if message["role"] == "assistant":
                    print(message["content"])
    except Exception as e:
        print(f"Error running Agent: {e}")

    # Stop server
    await server_service.async_stop_server()
    print("Example completed")


if __name__ == "__main__":
    print("MCP Custom Tools Example\n")

    print("=" * 60)
    print("Example: Creating and Testing Custom Tools")
    print("=" * 60)
    asyncio.run(custom_tools_demo())

    # Requires valid API key to run
    # print("\n" + "=" * 60)
    # print("Example: Agent with Custom Tools")
    # print("=" * 60)
    # asyncio.run(agent_with_custom_tools())
