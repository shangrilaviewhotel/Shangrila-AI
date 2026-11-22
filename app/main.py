from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.ai import ask_ai, client, AI_MODEL

import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path


# ----------------------------
# Initialize Firebase
# ----------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()


# ----------------------------
# FastAPI
# ----------------------------
app = FastAPI(
    title="Shangrila AI",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# Models
# ----------------------------
class ChatRequest(BaseModel):
    message: str


# ----------------------------
# Hotel assistant routes (unchanged purpose)
# ----------------------------
@app.get("/")
def home():
    return {
        "message": "Welcome to Shangrila AI!"
    }


@app.get("/test-firestore")
def test_firestore():
    rooms = db.collection("rooms").stream()
    room_list = []

    for room in rooms:
        data = room.to_dict()
        data["id"] = room.id
        room_list.append(data)

    return {
        "success": True,
        "totalRooms": len(room_list),
        "rooms": room_list
    }


@app.post("/chat")
def chat(request: ChatRequest):
    answer = ask_ai(request.message)
    return {"reply": answer}


# ----------------------------
# Private workspace UI and assistant
# This profile is deliberately separate from the hotel prompt and data.
# Tool integrations will be added behind explicit permissions in later steps.
# ----------------------------
WORKSPACE_FILE = Path(__file__).resolve().parent.parent / "workspace" / "index.html"

WORKSPACE_SYSTEM_PROMPT = """
You are the user's private general-purpose AI workspace assistant.
You help with software development, debugging, website maintenance, research,
planning, writing, and designing safe automations.
This is a personal workspace, not the Shangrila View Hotel guest assistant.
Do not assume access to files, repositories, accounts, or external tools.
Never claim to have changed, deployed, published, sent, or deleted anything
unless a connected tool has actually completed that action.
Ask for confirmation before destructive or externally visible actions.
Keep private workspace context separate from hotel guest data.
"""


@app.get("/workspace", response_class=HTMLResponse)
def workspace():
    if not WORKSPACE_FILE.is_file():
        return HTMLResponse("<h1>Workspace UI is not installed.</h1>", status_code=503)
    return HTMLResponse(WORKSPACE_FILE.read_text(encoding="utf-8"))


@app.get("/workspace/status")
def workspace_status():
    return {
        "workspace": "ready",
        "provider": AI_PROVIDER,
        "model": AI_MODEL,
        "tools_enabled": False,
        "note": "The standalone chat UI is ready. External tools are not connected yet."
    }


@app.post("/workspace/chat")
def workspace_chat(request: ChatRequest):
    message = request.message.strip()
    if not message:
        return {"reply": "Enter a message to begin."}

    response = client.chat.completions.create(
        model=AI_MODEL,
        messages=[
            {"role": "system", "content": WORKSPACE_SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]
    )
    return {"reply": response.choices[0].message.content or ""}
