"""
MCP Toolkit Prompt Definitions

This module defines various prompts used in the MCP toolkit, including server operations, tool management, client operations, etc.
These prompts are used to guide users in correctly using tools, providing input formats, examples, and explanations of common errors.

Module organization:
- Server basic operation prompts: creating, starting, stopping servers, etc.
- Server tool management prompts: adding tools, resources, and prompts, etc.
- Client operation prompts: creating clients, calling tools, managing resources, etc.
- LangChain integration prompts: getting LangChain-formatted tools and prompts

These prompts are referenced by the corresponding tool classes, used to generate the description field for tools, helping users understand how to use the tools.
"""

# Basic server operations
SERVER_CREATE_PROMPT = """
This tool is used to create a new MCP server instance.

**Input Format**:
- Hostname (default is localhost)
- Port number (default is 8000)
- Server configuration (optional, JSON format)

**Configuration Options**:
- host: Server host address
- port: Server port
- transport: Transport type (sse or stdio)
- command: Start command (only used for stdio mode)

Example input:
localhost 8000 {"transport": "sse"}

**Output**: Returns server instance information on success, error message on failure.
"""

START_SERVER_PROMPT = """
This tool is used to start an MCP server.

**Input Format**:
- Hostname (default is localhost)
- Port number (default is 8000)

Example input:
localhost 8000

**Output**: Returns server URL on success, error message on failure.
"""

STOP_SERVER_PROMPT = """
This tool is used to stop the currently running MCP server. No parameters are required.

**Note**: Make sure to save all necessary data before stopping the server, all connections will be disconnected after stopping.

**Output**: Returns success message on success, or appropriate message if server is not running.
"""

GET_SERVER_URL_PROMPT = """
This tool is used to get the URL of the currently running MCP server. No parameters are required.

**Note**: The server must be started to get the URL.

**Output**: Returns the full URL if the server is running; otherwise returns an error message.
"""

# Server tool management
ADD_TOOL_PROMPT = """
This tool is used to add a tool to the MCP server.

**Very Important**: You must provide input in the following format:
1. Tool name (short and descriptive)
2. Tool description (to help users understand the tool's functionality)
3. Tool code (Python function that accepts kwargs)
4. Code type (default is python)

**Code Requirements**:
- Function must receive parameters via kwargs
- Should handle missing or invalid parameters
- Return value should be a string or object that can be serialized to JSON

Complete example:
name: weather
description: Get weather for specified city
code:
```python
import requests

api_key = "demo_key"
location = kwargs.get("location", "New York")
url = f"https://api.example.com/weather?location={location}&appid={api_key}"

response = requests.get(url)
data = response.json()

if response.status_code == 200:
    temp = data["main"]["temp"]
    conditions = data["weather"][0]["description"]
    return f"Weather in {location}: {temp}°C, {conditions}"
else:
    return f"Unable to get weather information for {location}"
```

**Common Errors**:
- Ensure code syntax is correct and without indentation errors
- Ensure all libraries used are available in the server environment
- Handle all possible errors and exceptions
"""

ADD_RESOURCE_PROMPT = """
This tool is used to add a resource to the MCP server.

**Input Format**:
1. Resource name (must be unique)
2. Resource content (text, JSON object, or array)
3. MIME type (optional)

**Resource Content Requirements**:
- If providing JSON, ensure format is correct
- Large resources may need to be added in segments

Example input:
city_codes {"new_york": "101010100", "los_angeles": "101020100"}

**Common Errors**:
- Resource name already exists (will overwrite existing resource)
- Invalid JSON format
- Server not started

**Output**: Confirmation message for successful addition or error message.
"""

ADD_PROMPT_PROMPT = """
This tool is used to add prompt templates to the MCP server.

**Input Format**:
1. Prompt name (must be unique)
2. Prompt content (supports variables in {parameter} format)

**Tip**:
- Prompt content can contain variables in the format {variable_name}
- These variables will be replaced with actual values when used

Example input:
weather_prompt Please provide weather information for {location}

**Output**: Confirmation message for successful addition or error message.
"""

# Client operations
CREATE_CLIENT_PROMPT = """
This tool is used to create an MCP client and connect to a server.

**Very Important**: You must provide valid server information:
1. Server URL (must include protocol, host, and optional port)
2. Transport type (optional, default is "sse")

**Input Validation**:
- Server URL must be a valid HTTP/HTTPS URL
- Transport type must be either 'sse' or 'stdio'

Example input:
http://localhost:8000 sse

**Common Errors**:
- Server does not exist or is not running
- URL format error
- Transport type not supported

**Output**: Connection success message or error details.
"""

CALL_TOOL_PROMPT = """
This tool is used to call a tool on the MCP server.

**Very Important**: You must provide input in the following format:
1. Tool name (must be an existing tool on the server)
2. Tool parameters (JSON format object)

**Input Format**:
tool_name {"param1": "value1", "param2": "value2"}

Example input:
weather {"location": "New York"}

**Notes**:
- Ensure parameter names and types match the tool requirements
- JSON must be formatted correctly (double quotes, no trailing commas, etc.)

**Output**: Tool execution result or error message.
"""

LIST_TOOLS_PROMPT = """
This tool is used to list all available tools on the MCP server. No parameters are required.

**Use Cases**:
- Learn what tools are available on the server
- Get tool names and descriptions for calling

**Output Format**:
Returns a list of tools, each containing a name and description.

Example output:
[
  {"name": "weather", "description": "Get weather for a specified city"},
  {"name": "translate", "description": "Translate text"}
]
"""

LIST_RESOURCES_PROMPT = """
This tool is used to list all resources on the MCP server. No parameters are required.

**Use Cases**:
- View available resource list
- Get resource names for reading

**Output Format**:
Returns a list of resource names.

Example output:
["city_codes", "country_data", "templates"]
"""

READ_RESOURCE_PROMPT = """
This tool is used to read resource content from the MCP server.

**Input Format**:
- Resource name (must be an existing resource on the server)

Example input:
city_codes

**Notes**:
- Ensure the resource name exists, otherwise an error will be returned
- Large resources may need to be read in segments

**Output Format**:
Returns resource content and MIME type.
"""

LIST_PROMPTS_PROMPT = """
This tool is used to list all prompt templates on the MCP server. No parameters are required.

**Use Cases**:
- Learn what prompts are available on the server
- Get prompt names to retrieve specific content

**Output Format**:
Returns a list of prompt names.

Example output:
["weather_prompt", "greeting_prompt", "query_template"]
"""

GET_PROMPT_PROMPT = """
This tool is used to get specific prompt template content from the MCP server.

**Input Format**:
- Prompt name (must be an existing prompt on the server)

Example input:
weather_prompt

**Notes**:
- Ensure the prompt name exists, otherwise an error will be returned

**Output Format**:
Returns the complete prompt content string.
"""

GET_LANGCHAIN_TOOLS_PROMPT = """
This tool is used to get a LangChain tools list from the MCP server.

**Use Cases**:
- Get all available LangChain tools
- Understand the functionality and parameters of each tool

**Output Format**:
Returns a list of LangChain tools, each containing:
- name: Tool name
- description: Tool description
- args_schema: Parameter schema

Example output:
[
  {
    "name": "weather",
    "description": "Get weather for a specified city",
    "args_schema": {
      "location": {"type": "string", "description": "City name"}
    }
  }
]
"""

GET_LANGCHAIN_PROMPT_PROMPT = """
This tool is used to get a LangChain prompt from the MCP server.

**Input Format**:
- Prompt name (must be an existing prompt on the server)
- Prompt parameters (optional, JSON format)

**Parameter Description**:
- Prompt name: Name of the prompt template to retrieve
- Parameters: Variable values for filling the prompt template

Example input:
weather_prompt {"location": "New York"}

**Output Format**:
Returns a list of LangChain messages, including:
- System message (if any)
- User message
- Assistant message (if any)
"""
