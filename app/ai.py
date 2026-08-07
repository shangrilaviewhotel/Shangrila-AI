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

load_dotenv()

with open("data/hotel_profile.json", "r", encoding="utf-8") as f:
    hotel_data = json.load(f)

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


def ask_ai(message: str):

    # Detect hotel commands
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

    # Reload hotel data each request
    with open("data/hotel_profile.json", "r", encoding="utf-8") as f:
        hotel_data = json.load(f)

    # Normal AI conversation
    response = client.chat.completions.create(
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
                + "\n\nHotel Information:\n"
                + json.dumps(hotel_data, indent=2)
            },
            {
                "role": "user",
                "content": message
            }
        ]
    )

    return response.choices[0].message.content