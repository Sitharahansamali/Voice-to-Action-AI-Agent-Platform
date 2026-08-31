from transformers import pipeline
import os

_intent_pipeline = None

# Mapping clean candidate phrases to internal intent keys
INTENT_CANDIDATES = {
    "create a reminder": "create_reminder",
    "list my reminders": "list_reminders",
    "delete a reminder": "delete_reminder",
    "save a note": "save_note",
    "get my notes": "get_notes",
    "send an email": "send_email",
    "create a calendar event": "create_calendar_event",
    "search memory": "search_memory",
    "summarize meeting": "summarize_meeting",
    "general conversation": "general_conversation",
}

CONFIDENCE_THRESHOLD = 0.25

def get_intent_pipeline():
    global _intent_pipeline
    if _intent_pipeline is None:
        model_name = os.getenv("HF_MODEL_NAME", "joeddav/xlm-roberta-large-xnli")
        print(f"Initializing Hugging Face Intent Detector with model: {model_name}...")
        try:
            _intent_pipeline = pipeline("zero-shot-classification", model=model_name)
        except Exception as e:
            print(f"Failed to load {model_name}: {e}. Falling back to facebook/bart-large-mnli...")
            _intent_pipeline = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    return _intent_pipeline

def detect_intent(text: str) -> dict:
    text_clean = text.strip()
    if not text_clean:
        return {
            "intent": "general_conversation",
            "confidence": 0.0,
            "requires_clarification": True,
            "raw_label": None
        }

    classifier = get_intent_pipeline()
    labels = list(INTENT_CANDIDATES.keys())
    
    result = classifier(text_clean, labels)
    
    top_label = result["labels"][0]
    top_score = float(result["scores"][0])
    intent_key = INTENT_CANDIDATES.get(top_label, "general_conversation")
    
    requires_clarification = top_score < CONFIDENCE_THRESHOLD

    return {
        "intent": intent_key,
        "confidence": round(top_score, 4),
        "requires_clarification": requires_clarification,
        "raw_label": top_label
    }
