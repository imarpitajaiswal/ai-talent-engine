import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.agent.graph import agent_executor

app = FastAPI(title="AI Talent Engine")

# Explicitly add CORS and Allow Origins for cloud load balancers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Serve the Frontend UI
@app.get("/")
async def get_ui():
    with open("index.html", "r") as f:
        return HTMLResponse(f.read())

# 2. The WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Accept connection with explicit subprotocol/headers if requested
    await websocket.accept()
    
    state = {
        "chat_history": [],
        "current_question_index": 1,
        "total_questions": 3,
        "current_topic": "System Design and Asynchronous Architecture",
        "metrics": {"technical_depth": 0.0, "communication": 0.0, "problem_solving": 0.0},
        "interview_complete": False,
        "feedback_summary": ""
    }
    
    try:
        # Trigger the graph to generate the very first question
        state = agent_executor.invoke(state)
        first_question = state["chat_history"][-1]["content"]
        await websocket.send_json({"role": "Alex (CTO)", "content": first_question})
        
        while True:
            candidate_answer = await websocket.receive_text()
            state["chat_history"].append({"role": "candidate", "content": candidate_answer})
            
            if state["current_question_index"] > state["total_questions"]:
                state = agent_executor.invoke(state)
                metrics_data = state.get("metrics", {"technical_depth": 8.5, "communication": 9.0, "problem_solving": 8.8})
                feedback_text = state.get("feedback_summary", "Strong execution across distributed resilience, sharding protocols, and fault-tolerant worker mechanics.")
                
                await websocket.send_json({
                    "role": "Alex (CTO)",
                    "content": "CONCLUDED",
                    "is_complete": True,
                    "scores": metrics_data,
                    "critique": feedback_text
                })
                break
            
            state = agent_executor.invoke(state)
            next_question = state["chat_history"][-1]["content"]
            await websocket.send_json({"role": "Alex (CTO)", "content": next_question})
            
    except WebSocketDisconnect:
        print("Candidate disconnected.")
    except Exception as e:
        print(f"Server Error: {str(e)}")
        try:
            await websocket.send_json({"role": "System", "content": f"Session error: {str(e)}"})
        except:
            pass