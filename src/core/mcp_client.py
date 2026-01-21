"""
MCP Client for connecting to Model Context Protocol servers.

This module provides a client to interact with MCP servers that expose tools.
Supports both Node.js and Python-based MCP servers.
"""

import asyncio
from typing import Dict, List, Any, Optional


class MCPClientManager:
    """
    Manager for MCP clients with proper async lifecycle management.

    This manager maintains a single connection and reuses it for multiple operations.
    """

    def __init__(self, server_config: Dict[str, Any]):
        """
        Initialize the MCP client manager.

        Args:
            server_config: MCP server configuration
                {
                    "command": "python",
                    "args": ["-m", "mcp_weather_server"],
                    "env": None
                }
        """
        self.server_config = server_config
        self.session = None
        self.tools = []
        self.connected = False

    async def _connect(self):
        """Internal method to connect to MCP server."""
        if self.connected:
            return

        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client

            # Create server parameters
            server_params = StdioServerParameters(
                command=self.server_config["command"],
                args=self.server_config.get("args", []),
                env=self.server_config.get("env")
            )

            # Connect to server
            self.stdio_context = stdio_client(server_params)
            self.read_stream, self.write_stream = await self.stdio_context.__aenter__()

            # Create client session
            self.session = ClientSession(self.read_stream, self.write_stream)
            await self.session.__aenter__()

            # Initialize
            await self.session.initialize()

            self.connected = True

        except Exception as e:
            self.connected = False
            raise

    async def _disconnect(self):
        """Internal method to disconnect from MCP server."""
        if not self.connected:
            return

        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
            if hasattr(self, 'stdio_context'):
                await self.stdio_context.__aexit__(None, None, None)
            self.connected = False
        except Exception as e:
            pass  # Silently handle disconnect errors

    async def list_tools_async(self) -> List[Dict[str, Any]]:
        """
        List available tools from MCP server.

        Returns:
            List of tool definitions
        """
        await self._connect()

        try:
            tools_response = await self.session.list_tools()
            self.tools = tools_response.tools if hasattr(tools_response, 'tools') else []

            return [
                {
                    "name": tool.name,
                    "description": tool.description if hasattr(tool, 'description') else "",
                    "input_schema": tool.inputSchema if hasattr(tool, 'inputSchema') else {}
                }
                for tool in self.tools
            ]
        except Exception as e:
            print(f"Error listing tools: {e}")
            return []

    async def call_tool_async(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            Tool execution result as string
        """
        if not self.connected:
            await self._connect()

        try:
            result = await self.session.call_tool(tool_name, arguments)

            # Extract content from result
            if hasattr(result, 'content') and result.content:
                if isinstance(result.content, list) and len(result.content) > 0:
                    first_content = result.content[0]
                    if hasattr(first_content, 'text'):
                        return first_content.text
                    return str(first_content)
                return str(result.content)

            return str(result)

        except Exception as e:
            return f"Error calling tool {tool_name}: {str(e)}"

    async def execute_session(self, operations):
        """
        Execute multiple operations in a single session.

        Args:
            operations: Async function that performs operations with self

        Returns:
            Result from operations
        """
        try:
            await self._connect()
            result = await operations(self)
            return result
        finally:
            await self._disconnect()

    def run_sync(self, coro):
        """
        Run an async coroutine synchronously.

        Args:
            coro: Async coroutine to run

        Returns:
            Result of the coroutine
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            return loop.run_until_complete(coro)
        finally:
            # Clean up
            pass

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        Synchronously list tools.

        Returns:
            List of tool definitions
        """
        async def _list():
            result = await self.list_tools_async()
            await self._disconnect()
            return result

        return self.run_sync(_list())

    def execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Synchronously execute a tool call.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments

        Returns:
            Tool result as string
        """
        async def _execute():
            result = await self.call_tool_async(tool_name, arguments)
            await self._disconnect()
            return result

        return self.run_sync(_execute())

    def execute_multiple_tools(self, tool_calls: List[Dict[str, Any]]) -> List[str]:
        """
        Execute multiple tool calls in a single session.

        Args:
            tool_calls: List of {"tool": "name", "arguments": {...}}

        Returns:
            List of results
        """
        async def _execute_all(manager):
            results = []
            for call in tool_calls:
                result = await manager.call_tool_async(call["tool"], call["arguments"])
                results.append(result)
            return results

        return self.run_sync(self.execute_session(_execute_all))
