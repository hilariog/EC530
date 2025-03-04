from fastapi import FastAPI, HTTPException
from typing import List
from models import House, Room, User, Device

app = FastAPI()

# In-memory "database" storage and auto-increment counters
houses = {}
rooms = {}
users = {}
devices = {}

house_counter = 1
room_counter = 1
user_counter = 1
device_counter = 1

# ---------- USER ENDPOINTS ----------
@app.post("/users", response_model=User)
def create_user(user: User):
    global user_counter
    user.id = user_counter
    users[user_counter] = user
    user_counter += 1
    return user

@app.get("/users", response_model=List[User])
def get_all_users():
    return list(users.values())

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[user_id]

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    del users[user_id]
    return {"message": "User deleted successfully"}

# ---------- HOUSE ENDPOINTS ----------
@app.post("/houses", response_model=House)
def create_house(house: House):
    global house_counter
    house.id = house_counter
    houses[house_counter] = house
    house_counter += 1
    return house

@app.get("/houses", response_model=List[House])
def get_all_houses():
    return list(houses.values())

@app.get("/houses/{house_id}", response_model=House)
def get_house(house_id: int):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    return houses[house_id]

@app.delete("/houses/{house_id}")
def delete_house(house_id: int):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    del houses[house_id]
    return {"message": "House deleted successfully"}

# Endpoint to sell a house (change its owner)
@app.put("/houses/{house_id}/sell", response_model=House)
def sell_house(house_id: int, new_owner_id: int):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if new_owner_id not in users:
        raise HTTPException(status_code=404, detail="New owner (User) not found")
    house = houses[house_id]
    house.owner_id = new_owner_id
    return house

# ---------- ROOM ENDPOINTS ----------
@app.post("/rooms", response_model=Room)
def create_room(room: Room):
    global room_counter
    room.id = room_counter
    rooms[room_counter] = room
    room_counter += 1
    return room

@app.get("/rooms", response_model=List[Room])
def get_all_rooms():
    return list(rooms.values())

@app.get("/rooms/{room_id}", response_model=Room)
def get_room(room_id: int):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    return rooms[room_id]

@app.delete("/rooms/{room_id}")
def delete_room(room_id: int):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    del rooms[room_id]
    return {"message": "Room deleted successfully"}

# Endpoint to assign a user to a room
@app.put("/rooms/{room_id}/assign_user", response_model=Room)
def assign_user_to_room(room_id: int, user_id: int):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    room = rooms[room_id]
    user = users[user_id]
    if user_id in room.users:
        raise HTTPException(status_code=400, detail="User already assigned to this room")
    room.users.append(user_id)
    if room_id not in user.assigned_rooms:
        user.assigned_rooms.append(room_id)
    return room

# Endpoint to remove a user from a room
@app.put("/rooms/{room_id}/remove_user", response_model=Room)
def remove_user_from_room(room_id: int, user_id: int):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    room = rooms[room_id]
    user = users[user_id]
    if user_id not in room.users:
        raise HTTPException(status_code=400, detail="User not assigned to this room")
    room.users.remove(user_id)
    if room_id in user.assigned_rooms:
        user.assigned_rooms.remove(room_id)
    return room

# ---------- DEVICE ENDPOINTS ----------
@app.post("/devices", response_model=Device)
def create_device(device: Device):
    global device_counter
    device.id = device_counter
    devices[device_counter] = device
    device_counter += 1
    return device

@app.get("/devices", response_model=List[Device])
def get_all_devices():
    return list(devices.values())

@app.get("/devices/{device_id}", response_model=Device)
def get_device(device_id: int):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    return devices[device_id]

@app.delete("/devices/{device_id}")
def delete_device(device_id: int):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    del devices[device_id]
    return {"message": "Device deleted successfully"}

# Endpoints to update device status
@app.put("/devices/{device_id}/turn_on", response_model=Device)
def turn_on_device(device_id: int):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    device = devices[device_id]
    device.status = "on"
    return device

@app.put("/devices/{device_id}/turn_off", response_model=Device)
def turn_off_device(device_id: int):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    device = devices[device_id]
    device.status = "off"
    return device

# Endpoint to add a device to a room
@app.put("/rooms/{room_id}/add_device", response_model=Room)
def add_device_to_room(room_id: int, device_id: int):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    room = rooms[room_id]
    device = devices[device_id]
    if device_id in room.devices:
        raise HTTPException(status_code=400, detail="Device already in the room")
    room.devices.append(device_id)
    device.room_id = room_id
    return room

# Endpoint to remove a device from a room
@app.put("/rooms/{room_id}/remove_device", response_model=Room)
def remove_device_from_room(room_id: int, device_id: int):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    room = rooms[room_id]
    device = devices[device_id]
    if device_id not in room.devices:
        raise HTTPException(status_code=400, detail="Device not in the room")
    room.devices.remove(device_id)
    device.room_id = None
    return room
