import json

HOTEL_FILE = "data/hotel_profile.json"


def load_hotel():
    with open(HOTEL_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_hotel(data):
    with open(HOTEL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def add_room(number, room_type, price):
    hotel = load_hotel()

    hotel["rooms"].append(
        {
            "number": number,
            "type": room_type,
            "price": price,
            "status": "available"
        }
    )

    save_hotel(hotel)

    return f"Room {number} added successfully."


def remove_room(number):
    hotel = load_hotel()

    hotel["rooms"] = [
        room
        for room in hotel["rooms"]
        if room["number"] != number
    ]

    save_hotel(hotel)

    return f"Room {number} removed."


def change_price(number, new_price):
    hotel = load_hotel()

    for room in hotel["rooms"]:
        if room["number"] == number:
            room["price"] = new_price

    save_hotel(hotel)

    return f"Room {number} updated."


def check_in(number):
    hotel = load_hotel()

    for room in hotel["rooms"]:
        if room["number"] == number:
            room["status"] = "occupied"

    save_hotel(hotel)

    return f"Room {number} checked in."


def check_out(number):
    hotel = load_hotel()

    for room in hotel["rooms"]:
        if room["number"] == number:
            room["status"] = "available"

    save_hotel(hotel)

    return f"Room {number} checked out."