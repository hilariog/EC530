# test_smart_house_api.py

import unittest
from smart_house_api import User, House, Room, Device, RoomNotFoundError, DeviceNotFoundError, UserNotFoundError

class TestSmartHouseAPI(unittest.TestCase):
    def setUp(self):
        # Create users
        self.user1 = User(user_id=1, name="Alice", email="alice@example.com")
        self.user2 = User(user_id=2, name="Bob", email="bob@example.com")
        
        # Create a house with an owner
        self.house = House(house_id=101, address="1234 Main St", owner=self.user1)
        
        # Create a room and device
        self.room1 = Room(room_id=201, name="Living Room")
        self.device1 = Device(device_id=301, device_type="Light", name="Ceiling Light")
        
        # Add room and device to the house
        self.house.add_room(self.room1)
        self.house.add_device(self.device1)

    def test_assign_user_to_room(self):
        # Assign user2 to room1 and verify bidirectional linkage.
        self.room1.assign_user(self.user2)
        self.assertIn(self.user2, self.room1.users)
        self.assertIn(self.room1, self.user2.assigned_rooms)

    def test_sell_house(self):
        # Test selling the house from user1 to user2.
        sale_message = self.house.sell_house(self.user2)
        self.assertEqual(self.house.owner, self.user2)
        self.assertIn("sold to", sale_message)

    def test_add_and_remove_device_from_room(self):
        # Add a device to the room and then remove it.
        self.room1.add_device(self.device1)
        self.assertIn(self.device1, self.room1.devices)
        self.room1.remove_device(self.device1)
        self.assertNotIn(self.device1, self.room1.devices)
        
        # Attempting to remove again should raise an error.
        with self.assertRaises(DeviceNotFoundError):
            self.room1.remove_device(self.device1)

    def test_device_operations(self):
        # Check initial status and then toggle the device.
        self.assertEqual(self.device1.status, "off")
        turn_on_msg = self.device1.turn_on()
        self.assertEqual(self.device1.status, "on")
        self.assertIn("ON", turn_on_msg)
        turn_off_msg = self.device1.turn_off()
        self.assertEqual(self.device1.status, "off")
        self.assertIn("OFF", turn_off_msg)

    def test_remove_user_from_room(self):
        # Assign user and then remove
        self.room1.assign_user(self.user2)
        self.room1.remove_user(self.user2)
        self.assertNotIn(self.user2, self.room1.users)
        self.assertNotIn(self.room1, self.user2.assigned_rooms)
        
        # Removing a non-existent user should raise an error.
        with self.assertRaises(UserNotFoundError):
            self.room1.remove_user(self.user2)

if __name__ == '__main__':
    unittest.main()
