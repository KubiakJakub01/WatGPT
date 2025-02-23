"""REST API for the LLM Engine.

Run the API server using the following command:
```bash
uvicorn watgpt.api:app --host 0.0.0.0 --port 8000 --reload
```
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .llm_engine import LLMEngine

app = FastAPI()
llm_engine = LLMEngine()


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    response: str


@app.post('/chat', response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Endpoint to handle chat queries.
    """
    try:
        response = llm_engine.chat(request.query)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get('/health')
def health_check():
    """
    Health check endpoint to verify API status.
    """
    return {'status': 'ok'}
