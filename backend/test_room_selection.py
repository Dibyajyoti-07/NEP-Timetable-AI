#!/usr/bin/env python3

import sys
sys.path.append('.')

from app.services.timetable.advanced_generator import AdvancedTimetableGenerator, TimeSlot

def test_room_selection():
    """Test room selection logic"""
    print("Testing room selection logic...")
    
    generator = AdvancedTimetableGenerator()
    generator.setup_cse_ai_ml_courses()
    generator.setup_groups_and_resources()
    generator.initialize_occupancy_tracking()
    
    print(f"\nAvailable rooms: {len(generator.rooms)}")
    for room in generator.rooms:
        print(f"  {room.id}: {room.name} (Lab: {room.is_lab}, Capacity: {room.capacity})")
    
    # Test slot
    test_slot = TimeSlot("Mon", 800, 850)  # 13:20-14:10
    print(f"\nTesting slot: {test_slot}")
    
    # Test room selection without any occupancy
    room_id = generator.find_suitable_room(60, False, test_slot)
    print(f"Selected room (empty schedule): {room_id}")
    
    # Occupy the first room
    if room_id:
        generator.room_occupancy[room_id].append(test_slot)
        print(f"Occupied room {room_id} at {test_slot}")
    
    # Test room selection again
    room_id2 = generator.find_suitable_room(60, False, test_slot)
    print(f"Selected room (after occupying first): {room_id2}")
    
    # Show occupancy status
    print("\nRoom occupancy:")
    for room_id, slots in generator.room_occupancy.items():
        print(f"  {room_id}: {len(slots)} slots occupied")
        for slot in slots:
            print(f"    - {slot}")

if __name__ == "__main__":
    test_room_selection()