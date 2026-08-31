from datetime import datetime
from app.db.database import get_database

class EmailMCPServer:
    """MCP Server for Email operations."""
    
    def __init__(self):
        self.server_name = "EmailMCPServer"

    def get_tool_definitions(self):
        return [
            {
                "name": "send_email",
                "description": "Send an email to a recipient with subject and body.",
                "parameters": {
                    "recipient": {"type": "string", "description": "Email recipient address"},
                    "subject": {"type": "string", "description": "Subject of the email"},
                    "body": {"type": "string", "description": "Body message of the email"}
                }
            },
            {
                "name": "list_emails",
                "description": "List recently sent or received emails.",
                "parameters": {}
            }
        ]

    def execute_tool(self, tool_name: str, arguments: dict) -> dict:
        db = get_database()
        emails_col = db["emails"]

        if tool_name == "send_email":
            recipient = arguments.get("recipient", "Unknown Recipient")
            subject = arguments.get("subject", "No Subject")
            body = arguments.get("body", "")

            doc = {
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "status": "sent",
                "sent_at": datetime.now().isoformat()
            }
            res = emails_col.insert_one(doc)
            return {
                "success": True,
                "message": f"Email successfully sent to {recipient}.",
                "data": {
                    "recipient": recipient,
                    "subject": subject,
                    "id": str(getattr(res, 'inserted_id', 'new'))
                }
            }

        elif tool_name == "list_emails":
            all_emails = list(emails_col.find({}))
            cleaned = []
            for e in all_emails:
                c = dict(e)
                if "_id" in c:
                    c["_id"] = str(c["_id"])
                cleaned.append(c)
            return {
                "success": True,
                "count": len(cleaned),
                "emails": cleaned
            }

        else:
            raise ValueError(f"Unknown tool '{tool_name}' on EmailMCPServer")
