from datetime import datetime
from app.db.database import get_database

class CalendarMCPServer:
    """MCP Server for Calendar scheduling operations."""
    
    def __init__(self):
        self.server_name = "CalendarMCPServer"

    def get_tool_definitions(self):
        return [
            {
                "name": "create_calendar_event",
                "description": "Create a new calendar event or meeting.",
                "parameters": {
                    "event_title": {"type": "string", "description": "Title of the calendar event"},
                    "start_time": {"type": "string", "description": "Date and time of the event"}
                }
            },
            {
                "name": "list_events",
                "description": "List upcoming scheduled calendar events.",
                "parameters": {}
            },
            {
                "name": "delete_event",
                "description": "Delete a calendar event.",
                "parameters": {
                    "event_title": {"type": "string", "description": "Title of the event to delete"}
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: dict) -> dict:
        db = get_database()
        events_col = db["events"]

        if tool_name == "create_calendar_event":
            event_title = arguments.get("event_title", "Untitled Event")
            start_time = arguments.get("start_time", "TBD")
            doc = {
                "event_title": event_title,
                "start_time": start_time,
                "created_at": datetime.now().isoformat()
            }
            res = events_col.insert_one(doc)
            return {
                "success": True,
                "message": f"Calendar event '{event_title}' created for {start_time}.",
                "data": {
                    "event_title": event_title,
                    "start_time": start_time,
                    "id": str(getattr(res, 'inserted_id', 'new'))
                }
            }

        elif tool_name == "list_events":
            all_events = list(events_col.find({}))
            cleaned = []
            for ev in all_events:
                c = dict(ev)
                if "_id" in c:
                    c["_id"] = str(c["_id"])
                cleaned.append(c)
            return {
                "success": True,
                "count": len(cleaned),
                "events": cleaned
            }

        elif tool_name == "delete_event":
            event_title = arguments.get("event_title", "")
            res = events_col.delete_many({"event_title": event_title})
            return {
                "success": True,
                "message": f"Deleted event matching '{event_title}'.",
                "deleted_count": getattr(res, 'deleted_count', 0)
            }

        else:
            raise ValueError(f"Unknown tool '{tool_name}' on CalendarMCPServer")
