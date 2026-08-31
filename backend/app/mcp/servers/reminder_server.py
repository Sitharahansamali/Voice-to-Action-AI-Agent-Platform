from datetime import datetime
from app.db.database import get_database

class ReminderMCPServer:
    """MCP Server for Reminder management."""
    
    def __init__(self):
        self.server_name = "ReminderMCPServer"

    def get_tool_definitions(self):
        return [
            {
                "name": "create_reminder",
                "description": "Create a new reminder with text detail and target time/date.",
                "parameters": {
                    "text": {"type": "string", "description": "The description/task of the reminder"},
                    "due_time": {"type": "string", "description": "Target time or date, e.g. tomorrow at 9 AM"}
                }
            },
            {
                "name": "list_reminders",
                "description": "List existing active reminders.",
                "parameters": {}
            },
            {
                "name": "delete_reminder",
                "description": "Delete a reminder by search text or ID.",
                "parameters": {
                    "query": {"type": "string", "description": "Keyword or ID of the reminder to delete"}
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: dict) -> dict:
        db = get_database()
        reminders_col = db["reminders"]

        if tool_name == "create_reminder":
            text = arguments.get("text", "")
            due_time = arguments.get("due_time", "Not specified")
            doc = {
                "text": text,
                "due_time": due_time,
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
            res = reminders_col.insert_one(doc)
            return {
                "success": True,
                "message": f"Reminder created successfully for {due_time}.",
                "data": {
                    "text": text,
                    "due_time": due_time,
                    "id": str(getattr(res, 'inserted_id', 'new'))
                }
            }

        elif tool_name == "list_reminders":
            reminders = list(reminders_col.find({}))
            # Serialize for JSON
            cleaned = []
            for r in reminders:
                c = dict(r)
                if "_id" in c:
                    c["_id"] = str(c["_id"])
                cleaned.append(c)
            return {
                "success": True,
                "count": len(cleaned),
                "reminders": cleaned
            }

        elif tool_name == "delete_reminder":
            query = arguments.get("query", "")
            res = reminders_col.delete_many({"text": query})
            return {
                "success": True,
                "message": f"Deleted reminders matching query: '{query}'.",
                "deleted_count": getattr(res, 'deleted_count', 0)
            }

        else:
            raise ValueError(f"Unknown tool '{tool_name}' on ReminderMCPServer")
