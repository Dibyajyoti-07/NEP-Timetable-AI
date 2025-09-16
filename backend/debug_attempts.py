#!/usr/bin/env python3
import asyncio
import sys
import os
from copy import deepcopy

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongodb import connect_to_mongo
from app.services.timetable.advanced_generator import AdvancedTimetableGenerator

async def debug_attempts():
    """Debug each generation attempt to see where it fails"""
    print("🔧 Debugging Generation Attempts")
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
        
        # Show loaded data summary
        lab_courses = [c for c in generator.courses if c.is_lab]
        theory_courses = [c for c in generator.courses if not c.is_lab]
        print(f"\n📚 Loaded: {len(theory_courses)} theory courses, {len(lab_courses)} lab courses")
        
        # Calculate total hours needed
        total_theory_hours = sum(c.hours_per_week for c in theory_courses)
        total_lab_hours = sum(c.hours_per_week for c in lab_courses)
        print(f"\n⏰ Total hours needed: {total_theory_hours}h theory + {total_lab_hours}h lab = {total_theory_hours + total_lab_hours}h")
        
        # Calculate available slots
        theory_slots = generator.rules.get_theory_slots()
        lab_slots = generator.rules.get_lab_slots()
        total_theory_capacity = len(theory_slots) * (50/60)  # Convert to hours
        total_lab_capacity = len(lab_slots) * 3  # 3 hours per lab slot
        print(f"\n📅 Available capacity: {total_theory_capacity:.1f}h theory + {total_lab_capacity}h lab = {total_theory_capacity + total_lab_capacity:.1f}h")
        
        if total_theory_hours > total_theory_capacity:
            print(f"\n⚠️ WARNING: Not enough theory slots! Need {total_theory_hours}h but only have {total_theory_capacity:.1f}h")
        
        if total_lab_hours > total_lab_capacity:
            print(f"\n⚠️ WARNING: Not enough lab slots! Need {total_lab_hours}h but only have {total_lab_capacity}h")
        
        # Manual attempt with detailed logging
        print("\n🚀 Starting manual generation attempt...")
        
        # Reset for attempt
        generator.initialize_occupancy_tracking()
        generator.schedule = []
        
        # Step 1: Schedule labs first
        print("\n🧪 Step 1: Scheduling labs...")
        lab_result = generator.schedule_labs_first()
        print(f"Lab scheduling result: {lab_result}")
        print(f"Lab sessions scheduled: {len([e for e in generator.schedule if e.is_lab])}")
        
        if not lab_result:
            print("❌ Lab scheduling failed!")
            return
        
        # Show lab schedule
        lab_entries = [e for e in generator.schedule if e.is_lab]
        if lab_entries:
            print("\nLab schedule:")
            for entry in lab_entries:
                print(f"  {entry.course_code} - {entry.group_id} - {entry.time_slot}")
        else:
            print("No lab sessions scheduled (this might be normal if no lab courses)")
        
        # Step 2: Schedule theory sessions
        print("\n📚 Step 2: Scheduling theory sessions...")
        
        # Sort theory courses by priority (heavy courses first)
        theory_courses.sort(key=lambda c: c.hours_per_week, reverse=True)
        
        for course in theory_courses:
            sessions_needed = course.get_session_structure()
            main_group = next(group for group in generator.groups if not group.is_subgroup)
            
            print(f"\n📖 Scheduling {course.code}: {course.hours_per_week}h/week -> {sessions_needed}")
            
            for i, session_duration in enumerate(sessions_needed):
                print(f"  Session {i+1} ({session_duration}min):")
                
                # Get available slots
                single_slots = generator.rules.get_theory_slots()
                double_slots = generator.rules.get_double_period_slots()
                available_slots = double_slots if session_duration == 100 else single_slots
                
                print(f"    Available slots: {len(available_slots)}")
                
                # Apply soft constraints
                filtered_slots = generator.apply_soft_constraints_to_slots(
                    available_slots, course, main_group.id
                )
                print(f"    After soft constraints: {len(filtered_slots)}")
                
                scheduled = False
                
                for j, slot in enumerate(filtered_slots[:5]):  # Check first 5 slots
                    print(f"    Checking slot {j+1}: {slot}")
                    
                    # Check daily constraints
                    daily_ok = generator.check_daily_constraints(main_group.id, slot.day, slot)
                    print(f"      Daily constraints: {daily_ok}")
                    
                    if not daily_ok:
                        continue
                    
                    # Find resources
                    faculty_id = generator.find_suitable_faculty(course.code)
                    room_id = generator.find_suitable_room(main_group.size, False)
                    print(f"      Faculty: {faculty_id}, Room: {room_id}")
                    
                    if not faculty_id or not room_id:
                        continue
                    
                    # Check availability
                    available = generator.is_slot_available(slot, room_id, faculty_id, main_group.id)
                    print(f"      Slot available: {available}")
                    
                    if available:
                        # Book the slot
                        generator.book_slot(slot, room_id, faculty_id, main_group.id)
                        
                        # Add to schedule
                        from app.services.timetable.advanced_generator import ScheduleEntry
                        entry = ScheduleEntry(
                            course_code=course.code,
                            course_name=course.name,
                            group_id=main_group.id,
                            faculty_id=faculty_id,
                            room_id=room_id,
                            time_slot=slot,
                            is_lab=False,
                            session_duration=session_duration
                        )
                        generator.schedule.append(entry)
                        print(f"      ✅ Scheduled at {slot}")
                        scheduled = True
                        break
                
                if not scheduled:
                    print(f"    ❌ Failed to schedule session {i+1} for {course.code}")
                    print(f"    This would cause the entire generation to fail.")
                    
                    # Show why it failed
                    print(f"    Debugging failure:")
                    for j, slot in enumerate(filtered_slots[:3]):
                        print(f"      Slot {j+1}: {slot}")
                        daily_ok = generator.check_daily_constraints(main_group.id, slot.day, slot)
                        faculty_id = generator.find_suitable_faculty(course.code)
                        room_id = generator.find_suitable_room(main_group.size, False)
                        available = generator.is_slot_available(slot, room_id, faculty_id, main_group.id) if faculty_id and room_id else False
                        print(f"        Daily: {daily_ok}, Faculty: {bool(faculty_id)}, Room: {bool(room_id)}, Available: {available}")
                    
                    # Write failure details to file
                    with open('failure_analysis.txt', 'w') as f:
                        f.write(f"Failed to schedule {course.code} session {i+1} ({session_duration}min)\n")
                        f.write(f"Available slots before filtering: {len(available_slots)}\n")
                        f.write(f"Available slots after soft constraints: {len(filtered_slots)}\n")
                        f.write(f"\nFirst 10 slots checked:\n")
                        for k, slot in enumerate(filtered_slots[:10]):
                            daily_ok = generator.check_daily_constraints(main_group.id, slot.day, slot)
                            faculty_id = generator.find_suitable_faculty(course.code)
                            room_id = generator.find_suitable_room(main_group.size, False)
                            available = generator.is_slot_available(slot, room_id, faculty_id, main_group.id) if faculty_id and room_id else False
                            f.write(f"  {k+1}. {slot}: Daily={daily_ok}, Faculty={bool(faculty_id)}, Room={bool(room_id)}, Available={available}\n")
                    
                    return
        
        print(f"\n✅ All courses scheduled successfully!")
        print(f"Total sessions: {len(generator.schedule)}")
        
        # Validate the schedule
        validation_result = generator.validate_schedule()
        print(f"\n📋 Validation: {len(validation_result['errors'])} errors, {len(validation_result['warnings'])} warnings")
        
        if validation_result['errors']:
            print("\nErrors:")
            for error in validation_result['errors']:
                print(f"  - {error}")
        
        # Write success details to file
        with open('success_analysis.txt', 'w') as f:
            f.write(f"Successfully scheduled all courses!\n")
            f.write(f"Total sessions: {len(generator.schedule)}\n")
            f.write(f"Validation errors: {len(validation_result['errors'])}\n")
            f.write(f"Validation warnings: {len(validation_result['warnings'])}\n")
            f.write("\nSchedule:\n")
            for entry in generator.schedule:
                f.write(f"  {entry.course_code} - {entry.group_id} - {entry.time_slot}\n")
            
    except Exception as e:
        print(f"\n💥 EXCEPTION OCCURRED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_attempts())