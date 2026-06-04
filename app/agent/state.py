from typing import TypedDict, List, Dict, Any

class InterviewState(TypedDict):
    # Core chat log tracking history alternating between 'interviewer' and 'candidate'
    chat_history: List[Dict[str, str]]
    
    # Track metrics inside the interview pipeline loop
    current_question_index: int
    total_questions: int
    current_topic: str  # e.g., "System Design", "Concurrency", "Agent Workflows"
    
    # Real-time evaluation scoring matrix (0.0 to 10.0 scale)
    metrics: Dict[str, float]  # Keys: 'technical_depth', 'communication', 'problem_solving'
    
    # Operational triggers
    interview_complete: bool
    feedback_summary: str