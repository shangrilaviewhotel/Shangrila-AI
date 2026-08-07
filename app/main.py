from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.ai import ask_ai

import firebase_admin
from firebase_admin import credentials, firestore


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
    version="1.0.0"
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
# Routes
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

    return {
        "reply": answer
    }