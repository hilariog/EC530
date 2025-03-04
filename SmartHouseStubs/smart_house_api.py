# smart_house_api.py

class SmartHouseError(Exception):
    """Base exception for smart house errors."""
    pass

class UserNotFoundError(SmartHouseError):
    """Raised when a user is not found."""
    pass

class RoomNotFoundError(SmartHouseError):
    """Raised when a room is not found."""
    pass

class DeviceNotFoundError(SmartHouseError):
    """Raised when a device is not found."""
    pass


class User:
    def __init__(self, user_id: int, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.assigned_rooms = []  # List of Room objects

    def assign_to_room(self, room: "Room"):
        """Assign the user to a room."""
        if room not in self.assigned_rooms:
            self.assigned_rooms.append(room)
        else:
            raise ValueError(f"User {self.name} is already assigned to room {room.name}")

    def remove_from_room(self, room: "Room"):
        """Remove the user from a room."""
        if room in self.assigned_rooms:
            self.assigned_rooms.remove(room)
        else:
            raise ValueError(f"User {self.name} is not assigned to room {room.name}")

    def __repr__(self):
        return f"<User {self.user_id}: {self.name}>"


class House:
    def __init__(self, house_id: int, address: str, owner: User):
        self.house_id = house_id
        self.address = address
        self.owner = owner
        self.rooms = []    # List of Room objects
        self.devices = []  # List of Device objects (that belong to the house as a whole)

    def sell_house(self, new_owner: User):
        """Sell the house by changing its owner."""
        self.owner = new_owner
        return f"House sold to {new_owner.name}"

    def add_room(self, room: "Room"):
        """Add a new room to the house."""
        if room not in self.rooms:
            self.rooms.append(room)
        else:
            raise ValueError(f"Room {room.name} already exists in the house.")

    def remove_room(self, room: "Room"):
        """Remove a room from the house."""
        if room in self.rooms:
            self.rooms.remove(room)
        else:
            raise RoomNotFoundError(f"Room {room.name} not found in the house.")

    def add_device(self, device: "Device"):
        """Add a device to the house."""
        if device not in self.devices:
            self.devices.append(device)
        else:
            raise ValueError(f"Device {device.name} already exists in the house.")

    def remove_device(self, device: "Device"):
        """Remove a device from the house."""
        if device in self.devices:
            self.devices.remove(device)
        else:
            raise DeviceNotFoundError(f"Device {device.name} not found in the house.")

    def __repr__(self):
        return f"<House {self.house_id}: {self.address}>"


class Room:
    def __init__(self, room_id: int, name: str):
        self.room_id = room_id
        self.name = name
        self.users = []    # List of User objects
        self.devices = []  # List of Device objects in the room

    def assign_user(self, user: User):
        """Assign a user to this room."""
        if user not in self.users:
            self.users.append(user)
            user.assign_to_room(self)
        else:
            raise ValueError(f"User {user.name} is already assigned to room {self.name}")

    def remove_user(self, user: User):
        """Remove a user from this room."""
        if user in self.users:
            self.users.remove(user)
            user.remove_from_room(self)
        else:
            raise UserNotFoundError(f"User {user.name} not found in room {self.name}")

    def add_device(self, device: "Device"):
        """Add a device to the room."""
        if device not in self.devices:
            self.devices.append(device)
        else:
            raise ValueError(f"Device {device.name} already exists in room {self.name}")

    def remove_device(self, device: "Device"):
        """Remove a device from the room."""
        if device in self.devices:
            self.devices.remove(device)
        else:
            raise DeviceNotFoundError(f"Device {device.name} not found in room {self.name}")

    def __repr__(self):
        return f"<Room {self.room_id}: {self.name}>"


class Device:
    def __init__(self, device_id: int, device_type: str, name: str):
        self.device_id = device_id
        self.device_type = device_type
        self.name = name
        self.status = "off"  # Default status is off

    def turn_on(self):
        """Turn on the device."""
        self.status = "on"
        return f"{self.name} is now ON."

    def turn_off(self):
        """Turn off the device."""
        self.status = "off"
        return f"{self.name} is now OFF."

    def __repr__(self):
        return f"<Device {self.device_id}: {self.name} ({self.device_type}) - {self.status}>"
