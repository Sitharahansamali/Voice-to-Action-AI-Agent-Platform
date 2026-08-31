import unittest
from app.services.intent_detector import detect_intent
from app.mcp.client import mcp_client
from app.agent.graph import run_agent_workflow
from app.memory.memory import save_memory, search_memory
from app.db.database import get_database

class TestVoiceToActionPipeline(unittest.TestCase):

    def test_01_intent_detection(self):
        res = detect_intent("Remind me tomorrow at 9 AM to call John.")
        self.assertEqual(res["intent"], "create_reminder")
        self.assertGreater(res["confidence"], 0.25)
        self.assertFalse(res["requires_clarification"])

        res_email = detect_intent("Send an email to john@example.com.")
        self.assertEqual(res_email["intent"], "send_email")

    def test_02_mcp_servers_and_client(self):
        tools = mcp_client.list_available_tools()
        tool_names = [t["name"] for t in tools]
        self.assertIn("create_reminder", tool_names)
        self.assertIn("save_note", tool_names)
        self.assertIn("send_email", tool_names)
        self.assertIn("create_calendar_event", tool_names)

        # Call reminder tool
        rem_res = mcp_client.call_tool("create_reminder", {"text": "Buy groceries", "due_time": "Today 5 PM"})
        self.assertTrue(rem_res["success"])
        self.assertIn("Reminder created", rem_res["message"])

    def test_03_langgraph_workflow_reminder(self):
        result = run_agent_workflow("Remind me tomorrow at 9 AM to call John.")
        self.assertEqual(result["intent"]["intent"], "create_reminder")
        self.assertEqual(result["tool_name"], "create_reminder")
        self.assertTrue(result["tool_result"]["success"])
        self.assertIn("Reminder created", result["response"])
        self.assertGreaterEqual(len(result["steps_log"]), 4)

    def test_04_memory_and_database(self):
        db = get_database()
        notes_col = db["notes"]
        doc = {"title": "Test Title", "content": "Test Content"}
        notes_col.insert_one(doc)

        fetched = notes_col.find({"title": "Test Title"})
        self.assertGreaterEqual(len(fetched), 1)

        mem_id = save_memory("test_type", "Test vector memory item")
        self.assertTrue(mem_id.startswith("mem_"))
        
        search_res = search_memory("Test vector memory")
        self.assertGreaterEqual(search_res["count"], 1)

if __name__ == "__main__":
    unittest.main()
