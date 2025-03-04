from pydantic import BaseModel
from typing import Optional, List

class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    assigned_rooms: List[int] = []  # List of Room IDs

class Room(BaseModel):
    id: Optional[int] = None
    name: str
    users: List[int] = []    # List of User IDs
    devices: List[int] = []  # List of Device IDs

class Device(BaseModel):
    id: Optional[int] = None
    name: str
    device_type: str
    status: str = "off"
    room_id: Optional[int] = None  # Associated Room ID

class House(BaseModel):
    id: Optional[int] = None
    address: str
    owner_id: int
    rooms: List[int] = []   # List of Room IDs
    devices: List[int] = [] # List of Device IDs (that belong to the house)
    users: List[int] = []   # List of User IDs
