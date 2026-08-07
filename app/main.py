from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.ai import ask_ai

app = FastAPI(
    title="Shangrila AI",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "message": "Welcome to Shangrila AI!"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    answer = ask_ai(request.message)

    return {
        "reply": answer
    }