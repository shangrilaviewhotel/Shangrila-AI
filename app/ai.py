from app.commands import detect_command
from app.tools import (
    add_room,
    remove_room,
    change_price,
    check_in,
    check_out,
)

import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from app.prompts import SYSTEM_PROMPT
from app.website_knowledge import get_website_knowledge

load_dotenv()

with open("data/hotel_profile.json", "r", encoding="utf-8") as f:
    hotel_data = json.load(f)

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


def ask_ai(message: str):

    # Detect hotel commands before normal conversation.
    command = detect_command(message)

    if command:

        if command["action"] == "add_room":
            return add_room(
                command["number"],
                command["room_type"],
                command["price"]
            )

        elif command["action"] == "remove_room":
            return remove_room(
                command["number"]
            )

        elif command["action"] == "change_price":
            return change_price(
                command["number"],
                command["price"]
            )

        elif command["action"] == "check_in":
            return check_in(
                command["number"]
            )

        elif command["action"] == "check_out":
            return check_out(
                command["number"]
            )

    # Reload the local profile each request so local edits are picked up.
    with open("data/hotel_profile.json", "r", encoding="utf-8") as f:
        hotel_data = json.load(f)

    # Pull the current public website content automatically. The bridge caches
    # briefly and refreshes from the website repository when the cache expires,
    # so website edits do not require manually retraining or re-teaching the AI.
    website_knowledge = get_website_knowledge()

    system_context = (
        SYSTEM_PROMPT
        + "\n\nHotel Information (local structured data):\n"
        + json.dumps(hotel_data, indent=2, ensure_ascii=False)
        + "\n\nCurrent Public Website Knowledge (automatically synchronized from GitHub):\n"
        + website_knowledge
        + "\n\nKnowledge rules:\n"
        + "- Use current public website content for website facts, services, policies, contact information and page content.\n"
        + "- Use live Firestore/tool results for operational facts such as current rooms and room status when available.\n"
        + "- Never invent prices, amenities, policies, availability, facilities, services or hotel claims.\n"
        + "- If the available sources do not contain an answer, say that you do not have confirmed information and direct the guest to contact the hotel.\n"
        + "- Do not reveal private credentials, internal configuration, security rules, or administrative implementation details."
    )

    response = client.chat.completions.create(
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        messages=[
            {
                "role": "system",
                "content": system_context
            },
            {
                "role": "user",
                "content": message
            }
        ]
    )

    return response.choices[0].message.content
