import json
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.agent.state import InterviewState
from app.agent.prompts import CTO_INTERVIEWER_PROMPT, EVALUATOR_PROMPT
from app.config import settings

# 1. Initialize the Updated Production LLMs
chat_llm = ChatGroq(api_key=settings.GROQ_API_KEY, model="llama-3.3-70b-versatile", temperature=0.7)
eval_llm = ChatGroq(api_key=settings.GROQ_API_KEY, model="llama-3.1-8b-instant", temperature=0).bind(response_format={"type": "json_object"})

def evaluator_node(state: InterviewState):
    """Silently grades the candidate's last answer and captures a detailed critique."""
    chat_history = state.get("chat_history", [])
    
    if not chat_history or chat_history[-1]["role"] == "interviewer":
        return {}

    candidate_answer = chat_history[-1]["content"]
    prompt = EVALUATOR_PROMPT
    
    try:
        response = eval_llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=candidate_answer)
        ])
        
        score_data = json.loads(response.content)
        
        # Capture the text critique alongside the raw metrics
        updated_metrics = {
            "technical_depth": score_data.get("technical_depth", 0.0),
            "communication": score_data.get("communication", 0.0),
            "problem_solving": score_data.get("problem_solving", 0.0)
        }
        
        # Store the critique into the state
        return {
            "metrics": updated_metrics,
            "feedback_summary": score_data.get("critique", "Solid response matching core criteria.")
        }
    except Exception as e:
        print(f"❌ Evaluator Error: {e}")
        return {}

def interviewer_node(state: InterviewState):
    """Acts as the CTO and generates the next interview question."""
    current_idx = state.get("current_question_index", 1)
    total_q = state.get("total_questions", 3)
    
    # Check if the interview limit has been reached before generating a question
    if current_idx > total_q:
        return {"interview_complete": True, "feedback_summary": "Interview concluded."}

    # Prepare the prompt with the current state context
    prompt = CTO_INTERVIEWER_PROMPT.format(
        current_topic=state.get("current_topic", "General Architecture"),
        question_index=current_idx,
        total_questions=total_q
    )
    
    # Build the message history for LangChain
    messages = [SystemMessage(content=prompt)]
    for msg in state.get("chat_history", []):
        if msg["role"] == "interviewer":
            messages.append(AIMessage(content=msg["content"]))
        else:
            messages.append(HumanMessage(content=msg["content"]))

    # Generate the next question
    response = chat_llm.invoke(messages)
    
    # Append the new question to the chat history
    new_history = state.get("chat_history", []) + [{"role": "interviewer", "content": response.content}]
    
    return {
        "chat_history": new_history,
        "current_question_index": current_idx + 1
    }

# 2. Define the Conditional Routing Logic
def route_interview_flow(state: InterviewState):
    """Determines whether to transition to END or continue looping back to evaluation."""
    if state.get("interview_complete") or state.get("current_question_index", 1) > state.get("total_questions", 3):
        return "end_session"
    return "continue_session"

# 3. Build the Modern LangGraph State Machine
workflow = StateGraph(InterviewState)

# Register our operational nodes
workflow.add_node("evaluator", evaluator_node)
workflow.add_node("interviewer", interviewer_node)

# START goes straight to evaluator to parse input state
workflow.add_edge(START, "evaluator")
# Evaluator always passes logical control sequentially to interviewer
workflow.add_edge("evaluator", "interviewer")

# Interrogate the routing edge logic to handle dynamic loop breaking
workflow.add_conditional_edges(
    "interviewer",
    route_interview_flow,
    {
        "end_session": END,
        "continue_session": "evaluator"
    }
)

# Compile the graph into an executable agent
agent_executor = workflow.compile()