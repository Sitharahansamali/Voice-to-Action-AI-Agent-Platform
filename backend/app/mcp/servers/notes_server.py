from datetime import datetime
from app.db.database import get_database

class NotesMCPServer:
    """MCP Server for Notes management."""
    
    def __init__(self):
        self.server_name = "NotesMCPServer"

    def get_tool_definitions(self):
        return [
            {
                "name": "save_note",
                "description": "Save or record a textual note.",
                "parameters": {
                    "content": {"type": "string", "description": "Content of the note"},
                    "title": {"type": "string", "description": "Optional title or category"}
                }
            },
            {
                "name": "get_notes",
                "description": "Get or search stored notes.",
                "parameters": {
                    "query": {"type": "string", "description": "Optional search term for filtering notes"}
                }
            },
            {
                "name": "delete_note",
                "description": "Delete notes matching a query.",
                "parameters": {
                    "query": {"type": "string", "description": "Search term or title of note to delete"}
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: dict) -> dict:
        db = get_database()
        notes_col = db["notes"]

        if tool_name == "save_note":
            content = arguments.get("content", "")
            title = arguments.get("title", "Quick Note")
            doc = {
                "title": title,
                "content": content,
                "created_at": datetime.now().isoformat()
            }
            res = notes_col.insert_one(doc)
            return {
                "success": True,
                "message": f"Note saved: '{title}'",
                "data": {
                    "title": title,
                    "content": content,
                    "id": str(getattr(res, 'inserted_id', 'new'))
                }
            }

        elif tool_name == "get_notes":
            query = arguments.get("query", "")
            all_notes = list(notes_col.find({}))
            cleaned = []
            for n in all_notes:
                c = dict(n)
                if "_id" in c:
                    c["_id"] = str(c["_id"])
                if not query or query.lower() in c.get("content", "").lower() or query.lower() in c.get("title", "").lower():
                    cleaned.append(c)
            return {
                "success": True,
                "count": len(cleaned),
                "notes": cleaned
            }

        elif tool_name == "delete_note":
            query = arguments.get("query", "")
            res = notes_col.delete_many({"title": query})
            return {
                "success": True,
                "message": f"Deleted notes with title: '{query}'.",
                "deleted_count": getattr(res, 'deleted_count', 0)
            }

        else:
            raise ValueError(f"Unknown tool '{tool_name}' on NotesMCPServer")
