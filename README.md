# AI Technical Interview Simulator 🚀

An autonomous, real-time interview simulator built with a multi-layered state-machine architecture. The application leverages **FastAPI WebSockets** for low-latency, bidirectional streaming and **LangGraph** to manage conversational loops, dynamic prompt adaptations, and background evaluation scoring.

## 🏗️ Architecture Blueprint

The system uses a cyclical state graph to split responsibilities cleanly between active engagement and analytical assessment:
1. **The Evaluator Node:** Silently extracts the candidate's responses, processes them via an LLM locked in structured JSON-mode, updates performance matrices, and generates critiques without adding lag to the chat.
2. **The Interviewer Node:** Examines the conversational history alongside candidate performance trends to generate contextual, high-pressure follow-up questions from a Startup CTO persona.

## 🛠️ Tech Stack
- **Framework:** FastAPI (Asynchronous WebSocket routing)
- **Agent Orchestration:** LangGraph & LangChain Core
- **LLM Engine:** Groq Cloud SDK (Llama 3.3 70B Versatile & Llama 3.1 8B Instant)
- **Environment & Standards:** Pydantic Settings v2 & Docker Containerization

## 💻 Local Setup Instructions

1. **Clone the Repo:**
   ```bash
   git clone [https://github.com/imarpitajaiswal/ai-talent-engine.git](https://github.com/imarpitajaiswal/ai-talent-engine.git)
   cd ai-talent-engine
