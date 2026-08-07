import re


def detect_command(message: str):
    text = message.lower().strip()

    # Add Room
    match = re.search(
        r"add room (\d+)\s+([a-zA-Z]+)\s+(\d+)",
        text
    )

    if match:
        return {
            "action": "add_room",
            "number": int(match.group(1)),
            "room_type": match.group(2).title(),
            "price": int(match.group(3))
        }

    # Remove Room
    match = re.search(r"remove room (\d+)", text)

    if match:
        return {
            "action": "remove_room",
            "number": int(match.group(1))
        }

    # Change Price
    match = re.search(
        r"change price (\d+)\s+(\d+)",
        text
    )

    if match:
        return {
            "action": "change_price",
            "number": int(match.group(1)),
            "price": int(match.group(2))
        }

    # Check In
    match = re.search(r"check in (\d+)", text)

    if match:
        return {
            "action": "check_in",
            "number": int(match.group(1))
        }

    # Check Out
    match = re.search(r"check out (\d+)", text)

    if match:
        return {
            "action": "check_out",
            "number": int(match.group(1))
        }

    return None