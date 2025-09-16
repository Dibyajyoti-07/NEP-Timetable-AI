#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongodb import connect_to_mongo
from app.services.timetable.advanced_generator import AdvancedTimetableGenerator

async def debug_scheduling():
    """Debug the scheduling process step by step"""
    print("🔧 Debugging Advanced Timetable Generation")
    print("=" * 60)
    
    # Connect to database
    await connect_to_mongo()
    
    # Test parameters
    program_id = "68b5c517e73858dcb11d37e4"
    semester = 5
    academic_setup = {
        "working_days": {
            "monday": True,
            "tuesday": True,
            "wednesday": True,
            "thursday": True,
            "friday": False,
            "saturday": False,
            "sunday": False
        },
        "time_settings": {
            "start_time": "09:00",
            "end_time": "17:00",
            "slot_duration": 50,
            "break_duration": 10,
            "lunch_break": True,
            "lunch_start": "13:00",
            "lunch_end": "14:00"
        }
    }
    
    try:
        # Create generator instance
        generator = AdvancedTimetableGenerator()
        
        # Load data from database
        print("\n📊 Loading data from database...")
        await generator.load_from_database_with_setup(program_id, semester, academic_setup)
        
        # Initialize occupancy tracking
        print("\n⚙️ Initializing occupancy tracking...")
        generator.initialize_occupancy_tracking()
        
        # Check available slots
        theory_slots = generator.rules.get_theory_slots()
        lab_slots = generator.rules.get_lab_slots()
        print(f"\n📅 Available slots: {len(theory_slots)} theory, {len(lab_slots)} lab")
        
        # Show first few theory slots
        print("\nFirst 10 theory slots:")
        for i, slot in enumerate(theory_slots[:10]):
            print(f"  {i+1}. {slot}")
        
        # Try to schedule labs first
        print("\n🧪 Scheduling labs first...")
        lab_result = generator.schedule_labs_first()
        print(f"Lab scheduling result: {lab_result}")
        
        # Show current schedule
        print(f"\nCurrent schedule has {len(generator.schedule)} entries:")
        for entry in generator.schedule:
            print(f"  {entry.course_code} - {entry.group_id} - {entry.time_slot}")
        
        # Try to schedule one theory course manually
        theory_courses = [course for course in generator.courses if not course.is_lab]
        if theory_courses:
            test_course = theory_courses[0]  # Take first theory course
            main_group = next(group for group in generator.groups if not group.is_subgroup)
            
            print(f"\n📚 Testing scheduling for {test_course.code} ({test_course.hours_per_week}h/week)")
            sessions_needed = test_course.get_session_structure()
            print(f"Sessions needed: {sessions_needed}")
            
            # Try to schedule first session
            session_duration = sessions_needed[0]
            available_slots = theory_slots if session_duration == 50 else generator.rules.get_double_period_slots()
            
            print(f"\nTrying to schedule {session_duration}min session...")
            print(f"Available slots: {len(available_slots)}")
            
            # Test first 5 slots
            for i, slot in enumerate(available_slots[:5]):
                print(f"\nTesting slot {i+1}: {slot}")
                
                # Check daily constraints
                daily_ok = generator.check_daily_constraints(main_group.id, slot.day, slot)
                print(f"  Daily constraints: {daily_ok}")
                
                # Check course repetition
                has_course = generator.has_course_on_day(test_course.code, main_group.id, slot.day)
                print(f"  Course already on {slot.day}: {has_course}")
                
                # Check constraint logic
                constraint_ok = not (session_duration < 100 and 
                                    test_course.hours_per_week <= 3 and 
                                    has_course)
                print(f"  Constraint check (duration<100 and hours<=3 and has_course): {not constraint_ok}")
                print(f"  Constraint result: {constraint_ok}")
                
                # Find resources
                faculty_id = generator.find_suitable_faculty(test_course.code)
                room_id = generator.find_suitable_room(main_group.size, False)
                print(f"  Faculty: {faculty_id}, Room: {room_id}")
                
                if faculty_id and room_id:
                    # Check availability
                    available = generator.is_slot_available(slot, room_id, faculty_id, main_group.id)
                    print(f"  Slot available: {available}")
                    
                    if available and daily_ok and constraint_ok:
                        print(f"  ✅ This slot would work!")
                        break
                else:
                    print(f"  ❌ Missing resources")
            
        # Write detailed results to file
        with open('debug_results.txt', 'w') as f:
            f.write(f"Theory slots: {len(theory_slots)}\n")
            f.write(f"Lab slots: {len(lab_slots)}\n")
            f.write(f"Lab scheduling result: {lab_result}\n")
            f.write(f"Current schedule entries: {len(generator.schedule)}\n")
            f.write("\nSchedule entries:\n")
            for entry in generator.schedule:
                f.write(f"  {entry.course_code} - {entry.group_id} - {entry.time_slot}\n")
        
        print("\nDetailed results written to debug_results.txt")
            
    except Exception as e:
        print(f"\n💥 EXCEPTION OCCURRED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_scheduling())