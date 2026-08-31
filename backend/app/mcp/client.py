from typing import Dict, Any, List
from app.mcp.servers.reminder_server import ReminderMCPServer
from app.mcp.servers.notes_server import NotesMCPServer
from app.mcp.servers.email_server import EmailMCPServer
from app.mcp.servers.calendar_server import CalendarMCPServer

class MCPClient:
    """MCP Client that manages connection to MCP Servers and invokes tools."""
    
    def __init__(self):
        self.servers = {}
        self._register_default_servers()

    def _register_default_servers(self):
        reminder_server = ReminderMCPServer()
        notes_server = NotesMCPServer()
        email_server = EmailMCPServer()
        calendar_server = CalendarMCPServer()

        self.register_server(reminder_server)
        self.register_server(notes_server)
        self.register_server(email_server)
        self.register_server(calendar_server)

    def register_server(self, server_instance):
        server_name = getattr(server_instance, 'server_name', server_instance.__class__.__name__)
        self.servers[server_name] = server_instance
        print(f"Registered MCP Server: {server_name}")

    def list_available_tools(self) -> List[Dict[str, Any]]:
        all_tools = []
        for server_name, server in self.servers.items():
            if hasattr(server, "get_tool_definitions"):
                tools = server.get_tool_definitions()
                for tool in tools:
                    t_copy = dict(tool)
                    t_copy["server"] = server_name
                    all_tools.append(t_copy)
        return all_tools

    def find_server_for_tool(self, tool_name: str):
        for server_name, server in self.servers.items():
            if hasattr(server, "get_tool_definitions"):
                for tool in server.get_tool_definitions():
                    if tool["name"] == tool_name:
                        return server
        return None

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        server = self.find_server_for_tool(tool_name)
        if not server:
            return {
                "success": False,
                "error": f"No registered MCP Server found for tool '{tool_name}'",
                "tool_name": tool_name
            }
        
        try:
            print(f"MCP Client invoking tool '{tool_name}' on server '{server.__class__.__name__}' with args: {arguments}")
            result = server.execute_tool(tool_name, arguments)
            result["executed_via"] = "MCP Client -> " + server.__class__.__name__
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}",
                "tool_name": tool_name
            }

# Singleton instance
mcp_client = MCPClient()
