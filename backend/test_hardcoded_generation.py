#!/usr/bin/env python3

import sys
sys.path.append('.')

from app.services.timetable.advanced_generator import AdvancedTimetableGenerator

def test_hardcoded_generation():
    """Test timetable generation with hardcoded data"""
    print("Testing timetable generation with hardcoded setup...")
    
    generator = AdvancedTimetableGenerator()
    
    # Use hardcoded setup instead of database
    generator.setup_cse_ai_ml_courses()
    generator.setup_groups_and_resources()
    
    print(f"\nSetup complete:")
    print(f"  Courses: {len(generator.courses)}")
    print(f"  Groups: {len(generator.groups)}")
    print(f"  Rooms: {len(generator.rooms)}")
    print(f"  Faculty: {len(generator.faculty)}")
    
    # Calculate resource requirements
    total_sessions = 0
    for course in generator.courses:
        sessions = course.get_session_structure()
        total_sessions += len(sessions)
        print(f"  {course.code}: {len(sessions)} sessions ({sessions})")
    
    theory_slots = generator.rules.get_theory_slots()
    theory_rooms = [r for r in generator.rooms if not r.is_lab]
    total_capacity = len(theory_slots) * len(theory_rooms)
    
    print(f"\nResource Analysis:")
    print(f"  Total sessions needed: {total_sessions}")
    print(f"  Theory slots per week: {len(theory_slots)}")
    print(f"  Theory rooms: {len(theory_rooms)}")
    print(f"  Total capacity: {total_capacity}")
    print(f"  Utilization: {(total_sessions/total_capacity)*100:.1f}%")
    
    # Try generation
    print("\nAttempting generation...")
    success = generator.generate_timetable()
    
    print(f"\nGeneration result: {'SUCCESS' if success else 'FAILED'}")
    
    if success:
        print(f"Generated {len(generator.schedule)} schedule entries:")
        for entry in generator.schedule:
            print(f"  {entry.course_code} - {entry.time_slot} - Room: {entry.room_id}")
    else:
        print("Generation failed. Check constraints and resource availability.")
    
    return success

if __name__ == "__main__":
    test_hardcoded_generation()