from firebase_admin import firestore


# Connect to Firebase Firestore
db = firestore.client()



# =====================================
# GET ALL ROOMS
# =====================================

def get_rooms():

    rooms = []

    docs = db.collection("rooms").stream()

    for doc in docs:

        room = doc.to_dict()

        room["id"] = doc.id

        rooms.append(room)


    return rooms




# =====================================
# ADD NEW ROOM
# =====================================

def add_room(room_number, room_type, price):

    room_data = {

        "roomNumber": str(room_number),

        "type": room_type,

        "price": int(price),

        "status": "available",

        "featured": False,

        "amenities": [],

        "images": [],

        "description": "",

        "discountPrice": None,

    }


    new_room = db.collection("rooms").document()


    new_room.set(room_data)


    return (
        f"Room {room_number} added successfully. "
        f"Type: {room_type}. Price: {price}"
    )





# =====================================
# REMOVE ROOM
# =====================================

def remove_room(room_number):

    rooms = db.collection("rooms").where(
        "roomNumber",
        "==",
        str(room_number)
    ).stream()



    found = False


    for room in rooms:

        room.reference.delete()

        found = True



    if found:

        return f"Room {room_number} removed successfully."



    return f"Room {room_number} was not found."







# =====================================
# UPDATE ROOM PRICE
# =====================================

def change_price(room_number, new_price):

    rooms = db.collection("rooms").where(
        "roomNumber",
        "==",
        str(room_number)
    ).stream()



    for room in rooms:

        room.reference.update(
            {
                "price": int(new_price)
            }
        )


        return (
            f"Room {room_number} price changed "
            f"to {new_price}"
        )



    return f"Room {room_number} not found."







# =====================================
# CHECK IN GUEST
# =====================================

def check_in(room_number):

    rooms = db.collection("rooms").where(
        "roomNumber",
        "==",
        str(room_number)
    ).stream()



    for room in rooms:

        room.reference.update(
            {
                "status": "occupied"
            }
        )


        return (
            f"Room {room_number} checked in."
        )



    return f"Room {room_number} not found."







# =====================================
# CHECK OUT GUEST
# =====================================

def check_out(room_number):

    rooms = db.collection("rooms").where(
        "roomNumber",
        "==",
        str(room_number)
    ).stream()



    for room in rooms:

        room.reference.update(
            {
                "status": "available"
            }
        )


        return (
            f"Room {room_number} checked out."
        )



    return f"Room {room_number} not found."







# =====================================
# UPDATE ANY ROOM FIELD
# =====================================

def update_room(room_number, updates):

    rooms = db.collection("rooms").where(
        "roomNumber",
        "==",
        str(room_number)
    ).stream()



    for room in rooms:

        room.reference.update(updates)


        return (
            f"Room {room_number} updated successfully."
        )



    return f"Room {room_number} not found."







# =====================================
# FIND ROOM
# =====================================

def find_room(room_number):

    rooms = db.collection("rooms").where(
        "roomNumber",
        "==",
        str(room_number)
    ).stream()



    for room in rooms:

        data = room.to_dict()

        data["id"] = room.id

        return data



    return None