# Usage Examples

## Basic Usage

Here's a basic example of using the MCP toolkit to connect to an MCP server and send a message:

```python
from langchain_mcp_toolkit.services import MCPClientService

# Initialize the client service
client_service = MCPClientService()

# Create a client and connect to the server
client_service.create(
    server_url="http://localhost:8000",
    api_key="your-api-key"
)

# Start a new conversation
conversation_id = client_service.start_conversation()

# Send a message and get a response
response = client_service.send_message("Hello, how are you?")
print(response)
```

## Using with LangChain

Here's how to use the MCP toolkit with LangChain:

```python
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain_mcp_toolkit.factory import MCPToolFactory

# Initialize the tool factory
tool_factory = MCPToolFactory(
    server_url="http://localhost:8000",
    api_key="your-api-key"
)

# Create MCP tools
conversation_tool = tool_factory.create_conversation_tool()
resource_tool = tool_factory.create_resource_tool()

# Initialize an agent with the tools
llm = OpenAI(temperature=0)
agent = initialize_agent(
    [conversation_tool, resource_tool],
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Run the agent
agent.run("Find information about machine learning and summarize it.")
```

## Managing MCP Servers

Here's how to manage MCP servers using the toolkit:

```python
from langchain_mcp_toolkit.services import MCPServerService

# Initialize the server service
server_service = MCPServerService()

# Create and start a server
server_config = {
    "host": "localhost",
    "port": 8000,
    "models": ["gpt-3.5-turbo"],
    "api_keys": ["your-api-key"],
}
server_service.create(server_config)
server_service.start_server()

# Check if the server is running
if server_service.is_running():
    print("Server is running!")
    print(server_service.get_server_info())

# Stop the server when done
server_service.stop_server()
``` 