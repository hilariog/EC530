import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import redis.asyncio as aioredis
from models import House, Room, User, Device
from typing import List

app = FastAPI()

# ── In-memory stores & auto-increment counters ─────────────────────────────────
houses, rooms, users, devices = {}, {}, {}, {}
house_ctr = room_ctr = user_ctr = device_ctr = 1

# ── Redis client (local or env REDIS_URL) ──────────────────────────────────────
REDIS_URL = "redis://localhost:6379/0"
redis = aioredis.from_url(REDIS_URL, decode_responses=True)

async def publish_topic(topic: str, message: dict):
    """Publish `message` to `topic` and record the topic name."""
    payload = json.dumps(message)
    await redis.sadd("topics", topic)
    await redis.publish(topic, payload)

async def event_stream(topic: str):
    """Server-Sent Events generator subscribing to a Redis channel."""
    pubsub = redis.pubsub()
    await pubsub.subscribe(topic)
    try:
        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if msg and msg.get("type") == "message":
                yield f"data: {msg['data']}\n\n"
            await asyncio.sleep(0.01)
    finally:
        await pubsub.unsubscribe(topic)
        await pubsub.close()

# ── Pub/Sub endpoints ─────────────────────────────────────────────────────────
@app.get("/topics")
async def list_topics():
    return list(await redis.smembers("topics"))

@app.post("/publish/{topic}")
async def manual_publish(topic: str, payload: dict):
    await publish_topic(topic, payload)
    return {"status": "published", "topic": topic, "message": payload}

@app.get("/subscribe/{topic}")
async def subscribe(topic: str):
    return StreamingResponse(event_stream(topic), media_type="text/event-stream")

# ── USER endpoints (publish on changes) ───────────────────────────────────────
@app.post("/users", response_model=User)
async def create_user(user: User):
    global user_ctr
    user.id = user_ctr; users[user_ctr] = user; user_ctr += 1
    await publish_topic("users", {"action": "create", "user": user.dict()})
    return user

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    if user_id not in users:
        raise HTTPException(404, "User not found")
    user = users.pop(user_id)
    await publish_topic("users", {"action": "delete", "user": {"id": user_id}})
    return {"message": "User deleted"}

# ── HOUSE endpoints ───────────────────────────────────────────────────────────
@app.post("/houses", response_model=House)
async def create_house(house: House):
    global house_ctr
    house.id = house_ctr; houses[house_ctr] = house; house_ctr += 1
    await publish_topic("houses", {"action": "create", "house": house.dict()})
    return house

@app.delete("/houses/{house_id}")
async def delete_house(house_id: int):
    if house_id not in houses:
        raise HTTPException(404, "House not found")
    houses.pop(house_id)
    await publish_topic("houses", {"action": "delete", "house": {"id": house_id}})
    return {"message": "House deleted"}

# ── ROOM endpoints ────────────────────────────────────────────────────────────
@app.post("/rooms", response_model=Room)
async def create_room(room: Room):
    global room_ctr
    room.id = room_ctr; rooms[room_ctr] = room; room_ctr += 1
    await publish_topic("rooms", {"action": "create", "room": room.dict()})
    return room

@app.put("/rooms/{room_id}/assign_user", response_model=Room)
async def assign_user(room_id: int, user_id: int):
    if room_id not in rooms or user_id not in users:
        raise HTTPException(404, "Not found")
    room = rooms[room_id]
    if user_id not in room.users:
        room.users.append(user_id)
        users[user_id].assigned_rooms.append(room_id)
        await publish_topic("rooms", {"action": "assign_user", "room_id": room_id, "user_id": user_id})
    return room

# ── DEVICE endpoints ──────────────────────────────────────────────────────────
@app.post("/devices", response_model=Device)
async def create_device(device: Device):
    global device_ctr
    device.id = device_ctr; devices[device_ctr] = device; device_ctr += 1
    await publish_topic("devices", {"action": "create", "device": device.dict()})
    return device

@app.put("/devices/{device_id}/turn_on", response_model=Device)
async def turn_on_device(device_id: int):
    if device_id not in devices:
        raise HTTPException(404, "Device not found")
    devices[device_id].status = "on"
    updated = devices[device_id]
    await publish_topic("devices", {"action": "turn_on", "device": updated.dict()})
    return updated

@app.put("/devices/{device_id}/turn_off", response_model=Device)
async def turn_off_device(device_id: int):
    if device_id not in devices:
        raise HTTPException(404, "Device not found")
    devices[device_id].status = "off"
    updated = devices[device_id]
    await publish_topic("devices", {"action": "turn_off", "device": updated.dict()})
    return updated
