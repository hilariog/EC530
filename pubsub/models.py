from pydantic import BaseModel
from typing import Optional, List

class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    assigned_rooms: List[int] = []

class Room(BaseModel):
    id: Optional[int] = None
    name: str
    users: List[int] = []
    devices: List[int] = []

class Device(BaseModel):
    id: Optional[int] = None
    name: str
    device_type: str
    status: str = "off"
    room_id: Optional[int] = None

class House(BaseModel):
    id: Optional[int] = None
    address: str
    owner_id: int
    rooms: List[int] = []
    devices: List[int] = []
    users: List[int] = []
