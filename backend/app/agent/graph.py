from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from app.services.intent_detector import detect_intent
from app.mcp.client import mcp_client
from app.memory.memory import save_memory, search_memory
import re

class AgentState(TypedDict):
    input_text: str
    intent_data: Dict[str, Any]
    memory_context: List[Dict[str, Any]]
    tool_name: Optional[str]
    tool_arguments: Dict[str, Any]
    tool_result: Optional[Dict[str, Any]]
    final_response: str
    steps_log: List[Dict[str, Any]]

# Extraction helpers
def extract_reminder_args(text: str) -> Dict[str, Any]:
    # e.g. "Remind me tomorrow at 9 AM to call John"
    time_keywords = ["tomorrow at 9 AM", "tomorrow at 9:00 AM", "tomorrow", "today", "at 9 AM", "next Monday"]
    due_time = "Not specified"
    clean_text = text
    
    # Try finding time expressions
    for kw in time_keywords:
        if kw.lower() in text.lower():
            due_time = kw
            break

    # Look for "to <action>"
    match = re.search(r'\bto\s+(.+)', text, re.IGNORECASE)
    if match:
        task_text = match.group(1).strip()
    else:
        # strip common prefix
        task_text = re.sub(r'^(remind me|create a reminder|reminder)\s*', '', text, flags=re.IGNORECASE).strip()

    return {
        "text": task_text if task_text else text,
        "due_time": due_time
    }

def extract_note_args(text: str) -> Dict[str, Any]:
    match = re.search(r'\b(note|that)\s+(.+)', text, re.IGNORECASE)
    if match:
        content = match.group(2).strip()
    else:
        content = re.sub(r'^(save note|create note|save a note)\s*', '', text, flags=re.IGNORECASE).strip()
    return {
        "title": "Quick Note",
        "content": content if content else text
    }

def extract_email_args(text: str) -> Dict[str, Any]:
    # e.g. "Send email to john@example.com about meeting"
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    recipient = email_match.group(0) if email_match else "recipient"
    return {
        "recipient": recipient,
        "subject": "Action Request",
        "body": text
    }

def extract_calendar_args(text: str) -> Dict[str, Any]:
    return {
        "event_title": text,
        "start_time": "Upcoming"
    }

# NODE 1: Intent Detection
def detect_intent_node(state: AgentState) -> AgentState:
    input_text = state["input_text"]
    intent_data = detect_intent(input_text)
    
    step_entry = {
        "step": "Intent Detection",
        "status": "completed",
        "details": f"Detected Intent: '{intent_data['intent']}' (Confidence: {intent_data['confidence']})"
    }
    
    return {
        **state,
        "intent_data": intent_data,
        "steps_log": state.get("steps_log", []) + [step_entry]
    }

# NODE 2: RAG Memory Retrieval
def memory_retrieval_node(state: AgentState) -> AgentState:
    input_text = state["input_text"]
    intent = state["intent_data"]["intent"]
    
    memory_results = []
    # Retrieve memory if intent is search_memory or prompt contains memory keywords
    if intent in ["search_memory", "get_notes", "list_reminders"] or any(k in input_text.lower() for k in ["yesterday", "last time", "history", "remember", "what did i"]):
        search_res = search_memory(input_text, n_results=3)
        memory_results = search_res.get("results", [])
        step_entry = {
            "step": "Memory Retrieval (RAG)",
            "status": "completed",
            "details": f"Retrieved {len(memory_results)} memory items from ChromaDB"
        }
    else:
        step_entry = {
            "step": "Memory Retrieval (RAG)",
            "status": "skipped",
            "details": "Historical context not required for this request"
        }

    return {
        **state,
        "memory_context": memory_results,
        "steps_log": state["steps_log"] + [step_entry]
    }

# NODE 3: Planner Node
def planner_node(state: AgentState) -> AgentState:
    intent_data = state["intent_data"]
    input_text = state["input_text"]
    intent = intent_data["intent"]
    
    if intent_data.get("requires_clarification", False):
        step_entry = {
            "step": "Planner",
            "status": "clarification_needed",
            "details": "Low intent confidence. Requesting user clarification."
        }
        return {
            **state,
            "tool_name": "clarification",
            "tool_arguments": {},
            "steps_log": state["steps_log"] + [step_entry]
        }

    tool_name = None
    args = {}

    if intent == "create_reminder":
        tool_name = "create_reminder"
        args = extract_reminder_args(input_text)
    elif intent == "list_reminders":
        tool_name = "list_reminders"
        args = {}
    elif intent == "delete_reminder":
        tool_name = "delete_reminder"
        args = {"query": input_text}
    elif intent == "save_note":
        tool_name = "save_note"
        args = extract_note_args(input_text)
    elif intent == "get_notes":
        tool_name = "get_notes"
        args = {"query": input_text}
    elif intent == "send_email":
        tool_name = "send_email"
        args = extract_email_args(input_text)
    elif intent == "create_calendar_event":
        tool_name = "create_calendar_event"
        args = extract_calendar_args(input_text)
    elif intent == "search_memory":
        tool_name = "none"
    else:
        tool_name = "none"

    step_entry = {
        "step": "Planner",
        "status": "completed",
        "details": f"Selected Tool: '{tool_name}' with args {args}" if tool_name != "none" else "No tool execution needed"
    }

    return {
        **state,
        "tool_name": tool_name,
        "tool_arguments": args,
        "steps_log": state["steps_log"] + [step_entry]
    }

# NODE 4: MCP Tool Execution Node
def tool_execution_node(state: AgentState) -> AgentState:
    tool_name = state.get("tool_name")
    tool_args = state.get("tool_arguments", {})
    
    if not tool_name or tool_name in ["none", "clarification"]:
        return state

    # Execute tool via MCP Client
    result = mcp_client.call_tool(tool_name, tool_args)
    
    # Save memory to ChromaDB
    try:
        save_memory(memory_type=tool_name, content=state["input_text"])
    except Exception as e:
        print(f"Vector memory save error: {e}")

    step_entry = {
        "step": "MCP Client & Server Tool Execution",
        "status": "completed" if result.get("success") else "failed",
        "details": result.get("message") or result.get("error") or str(result)
    }

    return {
        **state,
        "tool_result": result,
        "steps_log": state["steps_log"] + [step_entry]
    }

# NODE 5: Response Generation Node
def response_generation_node(state: AgentState) -> AgentState:
    tool_name = state.get("tool_name")
    tool_result = state.get("tool_result")
    intent_data = state.get("intent_data", {})
    memory_ctx = state.get("memory_context", [])
    input_text = state.get("input_text", "")

    if tool_name == "clarification":
        response = "I'm not completely sure what you'd like me to do. Could you clarify your request?"
    elif tool_result and tool_result.get("success"):
        response = tool_result.get("message", "Operation completed successfully.")
        if "reminders" in tool_result:
            count = tool_result.get("count", 0)
            items = [f"- {r.get('text')} ({r.get('due_time')})" for r in tool_result.get("reminders", [])]
            response = f"Found {count} reminder(s):\n" + "\n".join(items) if items else "You have no active reminders."
        elif "notes" in tool_result:
            count = tool_result.get("count", 0)
            items = [f"- {n.get('title')}: {n.get('content')}" for n in tool_result.get("notes", [])]
            response = f"Found {count} note(s):\n" + "\n".join(items) if items else "No notes found."
    elif tool_result and not tool_result.get("success"):
        response = f"Failed to execute operation: {tool_result.get('error')}"
    elif memory_ctx:
        mem_items = [f"- {m.get('content')}" for m in memory_ctx]
        response = f"Here is what I found in memory:\n" + "\n".join(mem_items)
    else:
        response = f"I understood your request ('{input_text}'). How else can I assist you?"

    step_entry = {
        "step": "Response Generation",
        "status": "completed",
        "details": response
    }

    return {
        **state,
        "final_response": response,
        "steps_log": state["steps_log"] + [step_entry]
    }

# Build LangGraph workflow
def build_agent_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("detect_intent", detect_intent_node)
    workflow.add_node("memory_retrieval", memory_retrieval_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("tool_execution", tool_execution_node)
    workflow.add_node("response_generation", response_generation_node)

    workflow.set_entry_point("detect_intent")
    workflow.add_edge("detect_intent", "memory_retrieval")
    workflow.add_edge("memory_retrieval", "planner")
    workflow.add_edge("planner", "tool_execution")
    workflow.add_edge("tool_execution", "response_generation")
    workflow.add_edge("response_generation", END)

    return workflow.compile()

# Singleton compiled graph
agent_graph = build_agent_graph()

def run_agent_workflow(input_text: str) -> Dict[str, Any]:
    initial_state = {
        "input_text": input_text,
        "intent_data": {},
        "memory_context": [],
        "tool_name": None,
        "tool_arguments": {},
        "tool_result": None,
        "final_response": "",
        "steps_log": []
    }
    
    final_state = agent_graph.invoke(initial_state)
    return {
        "input_text": final_state["input_text"],
        "intent": final_state["intent_data"],
        "tool_name": final_state.get("tool_name"),
        "tool_arguments": final_state.get("tool_arguments"),
        "tool_result": final_state.get("tool_result"),
        "response": final_state["final_response"],
        "steps_log": final_state["steps_log"]
    }
