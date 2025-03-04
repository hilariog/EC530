#test_smart_house_rest_api.py
import sys
import os

# Add the parent directory (the repository root) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Helper functions to create entities
def create_user(name, email):
    response = client.post("/users", json={"name": name, "email": email})
    assert response.status_code == 200
    return response.json()

def create_house(address, owner_id, rooms=[], devices=[], users=[]):
    response = client.post("/houses", json={
        "address": address,
        "owner_id": owner_id,
        "rooms": rooms,
        "devices": devices,
        "users": users
    })
    assert response.status_code == 200
    return response.json()

def create_room(name, users=[], devices=[]):
    response = client.post("/rooms", json={
        "name": name,
        "users": users,
        "devices": devices
    })
    assert response.status_code == 200
    return response.json()

def create_device(name, device_type):
    response = client.post("/devices", json={
        "name": name,
        "device_type": device_type
    })
    assert response.status_code == 200
    return response.json()


# ------------------------
# USER ENDPOINT TESTS
# ------------------------
def test_user_crud():
    # Create user
    user = create_user("Alice", "alice@example.com")
    user_id = user["id"]
    
    # Get all users (should contain at least this one)
    response = client.get("/users")
    assert response.status_code == 200
    users_list = response.json()
    assert any(u["id"] == user_id for u in users_list)
    
    # Get specific user
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Alice"
    
    # Delete user
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    # Verify deletion
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 404


# ------------------------
# HOUSE ENDPOINT TESTS
# ------------------------
def test_house_crud_and_sell():
    # Create two users for ownership changes
    owner1 = create_user("Bob", "bob@example.com")
    owner2 = create_user("Carol", "carol@example.com")
    
    # Create a house with owner1
    house = create_house("123 Main St", owner1["id"])
    house_id = house["id"]
    
    # Get all houses
    response = client.get("/houses")
    assert response.status_code == 200
    houses_list = response.json()
    assert any(h["id"] == house_id for h in houses_list)
    
    # Get specific house
    response = client.get(f"/houses/{house_id}")
    assert response.status_code == 200
    assert response.json()["address"] == "123 Main St"
    
    # Sell house to owner2 using query parameter new_owner_id
    response = client.put(f"/houses/{house_id}/sell", params={"new_owner_id": owner2["id"]})
    assert response.status_code == 200
    updated_house = response.json()
    assert updated_house["owner_id"] == owner2["id"]
    
    # Delete house
    response = client.delete(f"/houses/{house_id}")
    assert response.status_code == 200
    response = client.get(f"/houses/{house_id}")
    assert response.status_code == 404


# ------------------------
# ROOM ENDPOINT TESTS
# ------------------------
def test_room_crud_and_user_assignment():
    # Create a user and a room
    user = create_user("David", "david@example.com")
    room = create_room("Living Room")
    room_id = room["id"]
    
    # Get all rooms
    response = client.get("/rooms")
    assert response.status_code == 200
    rooms_list = response.json()
    assert any(r["id"] == room_id for r in rooms_list)
    
    # Get specific room
    response = client.get(f"/rooms/{room_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Living Room"
    
    # Assign user to room
    response = client.put(f"/rooms/{room_id}/assign_user", params={"user_id": user["id"]})
    assert response.status_code == 200
    updated_room = response.json()
    assert user["id"] in updated_room["users"]
    
    # Remove user from room
    response = client.put(f"/rooms/{room_id}/remove_user", params={"user_id": user["id"]})
    assert response.status_code == 200
    updated_room = response.json()
    assert user["id"] not in updated_room["users"]
    
    # Delete room
    response = client.delete(f"/rooms/{room_id}")
    assert response.status_code == 200
    response = client.get(f"/rooms/{room_id}")
    assert response.status_code == 404


# ------------------------
# DEVICE ENDPOINT TESTS
# ------------------------
def test_device_crud_and_status_update():
    # Create a device
    device = create_device("Thermostat", "TemperatureControl")
    device_id = device["id"]
    
    # Get all devices
    response = client.get("/devices")
    assert response.status_code == 200
    devices_list = response.json()
    assert any(d["id"] == device_id for d in devices_list)
    
    # Get specific device
    response = client.get(f"/devices/{device_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Thermostat"
    
    # Turn device on
    response = client.put(f"/devices/{device_id}/turn_on")
    assert response.status_code == 200
    assert response.json()["status"] == "on"
    
    # Turn device off
    response = client.put(f"/devices/{device_id}/turn_off")
    assert response.status_code == 200
    assert response.json()["status"] == "off"
    
    # Delete device
    response = client.delete(f"/devices/{device_id}")
    assert response.status_code == 200
    response = client.get(f"/devices/{device_id}")
    assert response.status_code == 404


# ------------------------
# ROOM-DEVICE ASSIGNMENT TESTS
# ------------------------
def test_add_and_remove_device_from_room():
    # Create a room and a device
    room = create_room("Bedroom")
    device = create_device("Lamp", "Lighting")
    room_id = room["id"]
    device_id = device["id"]
    
    # Add device to room
    response = client.put(f"/rooms/{room_id}/add_device", params={"device_id": device_id})
    assert response.status_code == 200
    updated_room = response.json()
    assert device_id in updated_room["devices"]
    
    # Check that the device now has room_id set
    response = client.get(f"/devices/{device_id}")
    assert response.status_code == 200
    assert response.json()["room_id"] == room_id
    
    # Remove device from room
    response = client.put(f"/rooms/{room_id}/remove_device", params={"device_id": device_id})
    assert response.status_code == 200
    updated_room = response.json()
    assert device_id not in updated_room["devices"]
    
    # Check that the device's room_id is reset
    response = client.get(f"/devices/{device_id}")
    assert response.status_code == 200
    assert response.json()["room_id"] is None

    
if __name__ == "__main__":
    pytest.main()
