import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.timetable.advanced_generator import AdvancedTimetableGenerator, SchedulingRules
from app.db.mongodb import db, connect_to_mongo
from bson import ObjectId

async def diagnose_constraints():
    print("=== CONSTRAINT DIAGNOSIS ===")
    
    # Connect to database
    await connect_to_mongo()
    
    # Use the known working data
    program_id = "68b5c517e73858dcb11d37e4"
    semester = 5
    
    print(f"Analyzing constraints for Program {program_id}, Semester {semester}")
    
    # Load raw data
    courses_cursor = db.db.courses.find({"program_id": ObjectId(program_id), "semester": semester})
    courses = await courses_cursor.to_list(length=None)
    
    groups_cursor = db.db.student_groups.find({"program_id": program_id})
    groups = await groups_cursor.to_list(length=None)
    
    rooms_cursor = db.db.rooms.find({})
    rooms = await rooms_cursor.to_list(length=None)
    
    faculty_cursor = db.db.faculty.find({})
    faculty = await faculty_cursor.to_list(length=None)
    
    print(f"\nRaw data loaded:")
    print(f"  - Courses: {len(courses)}")
    print(f"  - Groups: {len(groups)}")
    print(f"  - Rooms: {len(rooms)}")
    print(f"  - Faculty: {len(faculty)}")
    
    # Analyze courses in detail
    print(f"\nCourse Analysis:")
    total_hours = 0
    lab_hours = 0
    theory_hours = 0
    
    for course in courses:
        hours = course.get('hours_per_week', 0)
        is_lab = course.get('is_lab', False)
        total_hours += hours
        
        if is_lab:
            lab_hours += hours
        else:
            theory_hours += hours
            
        print(f"  - {course['code']}: {hours}h/week, Lab: {is_lab}")
    
    print(f"\nTotal weekly hours: {total_hours}")
    print(f"Lab hours: {lab_hours}")
    print(f"Theory hours: {theory_hours}")
    
    # Analyze groups
    print(f"\nGroup Analysis:")
    for group in groups:
        size = group.get('size', group.get('student_count', 'Unknown'))
        print(f"  - {group['name']}: {size} students")
        print(f"    Fields: {list(group.keys())}")
    
    # Analyze rooms
    print(f"\nRoom Analysis:")
    lab_rooms = []
    theory_rooms = []
    
    for room in rooms:
        capacity = room.get('capacity', 0)
        is_lab = room.get('is_lab', False)
        
        if is_lab:
            lab_rooms.append(room)
        else:
            theory_rooms.append(room)
            
        print(f"  - {room['name']}: Capacity {capacity}, Lab: {is_lab}")
    
    print(f"\nRoom summary: {len(lab_rooms)} lab rooms, {len(theory_rooms)} theory rooms")
    
    # Analyze faculty
    print(f"\nFaculty Analysis:")
    all_course_codes = [c['code'] for c in courses]
    faculty_coverage = {}
    
    for fac in faculty:
        subjects = fac.get('subjects', [])
        print(f"  - {fac['name']}: {subjects}")
        
        for subject in subjects:
            if subject in all_course_codes:
                faculty_coverage[subject] = faculty_coverage.get(subject, 0) + 1
    
    print(f"\nFaculty coverage:")
    uncovered_courses = []
    for course_code in all_course_codes:
        coverage = faculty_coverage.get(course_code, 0)
        print(f"  - {course_code}: {coverage} faculty members")
        if coverage == 0:
            uncovered_courses.append(course_code)
    
    if uncovered_courses:
        print(f"\n❌ CRITICAL: Courses without faculty: {uncovered_courses}")
    
    # Calculate time constraints
    print(f"\nTime Constraint Analysis:")
    
    # Assume 5 working days, 6 periods per day = 30 periods per week
    # Each period is typically 50 minutes
    available_periods_per_week = 5 * 6  # 30 periods
    available_minutes_per_week = available_periods_per_week * 50  # 1500 minutes
    available_hours_per_week = available_minutes_per_week / 60  # 25 hours
    
    print(f"Available time slots per week: {available_periods_per_week} periods ({available_hours_per_week} hours)")
    print(f"Required time per week: {total_hours} hours")
    
    if total_hours > available_hours_per_week:
        print(f"❌ CRITICAL: Not enough time slots! Need {total_hours}h but only have {available_hours_per_week}h")
    else:
        print(f"✅ Time constraint OK: {available_hours_per_week - total_hours}h buffer")
    
    # Check room capacity constraints
    print(f"\nRoom Capacity Analysis:")
    
    # Get actual group sizes
    group_sizes = []
    for group in groups:
        size = group.get('size', group.get('student_count', None))
        if isinstance(size, int):
            group_sizes.append(size)
    
    if group_sizes:
        max_group_size = max(group_sizes)
        suitable_rooms = [r for r in rooms if r.get('capacity', 0) >= max_group_size]
        
        print(f"Largest group: {max_group_size} students")
        print(f"Rooms that can accommodate: {len(suitable_rooms)} out of {len(rooms)}")
        
        if len(suitable_rooms) == 0:
            print(f"❌ CRITICAL: No rooms can accommodate the largest group!")
        
        # Check lab room capacity
        suitable_lab_rooms = [r for r in lab_rooms if r.get('capacity', 0) >= max_group_size]
        print(f"Lab rooms that can accommodate: {len(suitable_lab_rooms)} out of {len(lab_rooms)}")
        
        if lab_hours > 0 and len(suitable_lab_rooms) == 0:
            print(f"❌ CRITICAL: No lab rooms can accommodate groups, but lab courses exist!")
    
    # Try a minimal generation to see specific errors
    print(f"\n=== ATTEMPTING MINIMAL GENERATION ===")
    
    try:
        academic_setup = {
            "working_days": {
                "Monday": True,
                "Tuesday": True,
                "Wednesday": True,
                "Thursday": True,
                "Friday": True,
                "Saturday": False,
                "Sunday": False
            },
            "time_slots": {
                "start_time": "09:00",
                "end_time": "17:00",
                "break_duration": 60,
                "lunch_start": "13:00",
                "lunch_end": "14:00"
            },
            "constraints": {
                "max_periods_per_day": 8,  # Increased from 6
                "max_continuous_periods": 4,  # Increased from 3
                "min_break_between_periods": 5  # Reduced from 10
            }
        }
        
        rules = await SchedulingRules.from_database_with_setup(program_id, academic_setup)
        generator = AdvancedTimetableGenerator(rules)
        await generator.load_from_database_with_setup(program_id, semester, academic_setup)
        
        print(f"Generator setup complete")
        print(f"Available time slots: {len(rules.get_theory_slots())} theory, {len(rules.get_lab_slots())} lab")
        
        # Try just scheduling labs first
        print(f"\nTrying to schedule labs only...")
        generator.schedule = []
        generator.initialize_occupancy_tracking()
        
        lab_result = generator.schedule_labs_first()
        print(f"Lab scheduling result: {lab_result}")
        
        if hasattr(generator, 'schedule'):
            print(f"Lab sessions scheduled: {len([s for s in generator.schedule if s.is_lab])}")
        
        # Try scheduling theory
        print(f"\nTrying to schedule theory sessions...")
        theory_result = generator.schedule_theory_sessions()
        print(f"Theory scheduling result: {theory_result}")
        
        if hasattr(generator, 'schedule'):
            print(f"Total sessions scheduled: {len(generator.schedule)}")
            print(f"Theory sessions: {len([s for s in generator.schedule if not s.is_lab])}")
        
        # Validate
        validation = generator.validate_schedule()
        print(f"\nValidation result:")
        print(f"  Valid: {validation['valid']}")
        print(f"  Errors: {len(validation['errors'])}")
        print(f"  Warnings: {len(validation['warnings'])}")
        
        if validation['errors']:
            print(f"\nFirst 5 validation errors:")
            for i, error in enumerate(validation['errors'][:5]):
                print(f"  {i+1}. {error}")
        
    except Exception as e:
        print(f"Exception during generation: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n=== DIAGNOSIS COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(diagnose_constraints())