import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.timetable.advanced_generator import AdvancedTimetableGenerator, SchedulingRules
from app.db.mongodb import db, connect_to_mongo
from bson import ObjectId

async def detailed_debug():
    print("=== DETAILED DEBUG: Advanced Timetable Generation ===")
    
    # Connect to database
    await connect_to_mongo()
    
    print("\n1. Checking available data in database...")
    
    # Check all programs first
    programs_cursor = db.db.programs.find({})
    programs = await programs_cursor.to_list(length=None)
    print(f"Found {len(programs)} programs:")
    for program in programs:
        print(f"  - {program.get('name', 'Unknown')}: ID = {program['_id']}")
    
    # Check all courses
    all_courses_cursor = db.db.courses.find({})
    all_courses = await all_courses_cursor.to_list(length=None)
    print(f"\nFound {len(all_courses)} total courses:")
    program_course_count = {}
    for course in all_courses:
        prog_id = str(course.get('program_id', 'Unknown'))
        program_course_count[prog_id] = program_course_count.get(prog_id, 0) + 1
        if len(program_course_count) <= 3:  # Show details for first few
            print(f"  - {course['code']}: {course['name']} (Program: {prog_id}, Semester: {course.get('semester', 'N/A')})")
    
    print(f"\nCourses by program:")
    for prog_id, count in program_course_count.items():
        print(f"  - Program {prog_id}: {count} courses")
    
    # Use the first program that has courses
    if program_course_count:
        program_id = list(program_course_count.keys())[0]
        print(f"\nUsing program ID: {program_id}")
    else:
        print("\nNo courses found in database!")
        return
    
    # Check courses for this program
    semester = 1
    print(f"\n2. Loading data for Program {program_id}, Semester {semester}...")
    
    # Check courses
    courses_cursor = db.db.courses.find({"program_id": ObjectId(program_id), "semester": semester})
    courses = await courses_cursor.to_list(length=None)
    print(f"Found {len(courses)} courses:")
    for course in courses:
        print(f"  - {course['code']}: {course['name']} ({course['hours_per_week']}h/week, Lab: {course.get('is_lab', False)})")
    
    # If no courses for semester 1, try other semesters
    if len(courses) == 0:
        print("No courses for semester 1, checking other semesters...")
        for sem in [2, 3, 4, 5, 6, 7, 8]:
            courses_cursor = db.db.courses.find({"program_id": ObjectId(program_id), "semester": sem})
            courses = await courses_cursor.to_list(length=None)
            if len(courses) > 0:
                print(f"Found {len(courses)} courses in semester {sem}")
                semester = sem
                break
    
    if len(courses) == 0:
        print("No courses found for any semester!")
        return
    
    # Check student groups
    groups_cursor = db.db.student_groups.find({"program_id": program_id})
    groups = await groups_cursor.to_list(length=None)
    print(f"\nFound {len(groups)} student groups:")
    for group in groups:
        size = group.get('size', group.get('student_count', 'Unknown'))
        print(f"  - {group['name']}: {size} students")
    
    # Check rooms
    rooms_cursor = db.db.rooms.find({})
    rooms = await rooms_cursor.to_list(length=None)
    print(f"\nFound {len(rooms)} rooms:")
    for room in rooms:
        print(f"  - {room['name']}: Capacity {room['capacity']}, Lab: {room.get('is_lab', False)}")
    
    # Check faculty
    faculty_cursor = db.db.faculty.find({})
    faculty = await faculty_cursor.to_list(length=None)
    print(f"\nFound {len(faculty)} faculty:")
    for fac in faculty:
        print(f"  - {fac['name']}: Subjects {fac.get('subjects', [])}")
    
    # Check if we have enough resources
    print("\n3. Resource Analysis:")
    
    # Calculate total hours needed
    total_hours_needed = sum(course['hours_per_week'] for course in courses)
    print(f"Total hours needed per week: {total_hours_needed}")
    
    # Check lab requirements vs lab rooms
    lab_courses = [c for c in courses if c.get('is_lab', False)]
    lab_rooms = [r for r in rooms if r.get('is_lab', False)]
    print(f"Lab courses: {len(lab_courses)}, Lab rooms: {len(lab_rooms)}")
    
    # Check room capacities vs group sizes
    if groups:
        group_sizes = [group.get('size', group.get('student_count', 0)) for group in groups if isinstance(group.get('size', group.get('student_count', 0)), int)]
        if group_sizes:
            max_group_size = max(group_sizes)
            suitable_rooms = [r for r in rooms if r['capacity'] >= max_group_size]
            print(f"Max group size: {max_group_size}, Suitable rooms: {len(suitable_rooms)}")
        else:
            print(f"No valid group sizes found")
    
    # Check faculty coverage
    all_course_codes = [c['code'] for c in courses]
    faculty_subjects = []
    for fac in faculty:
        faculty_subjects.extend(fac.get('subjects', []))
    uncovered_courses = [code for code in all_course_codes if code not in faculty_subjects]
    print(f"Courses without faculty: {uncovered_courses}")
    
    print("\n4. Attempting generation...")
    
    # Create generator with correct academic setup format
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
            "max_periods_per_day": 6,
            "max_continuous_periods": 3,
            "min_break_between_periods": 10
        }
    }
    
    try:
        rules = await SchedulingRules.from_database_with_setup(program_id, academic_setup)
        generator = AdvancedTimetableGenerator(rules)
        
        # Load data
        await generator.load_from_database_with_setup(program_id, semester, academic_setup)
        
        print(f"Generator loaded:")
        print(f"  - Courses: {len(generator.courses)}")
        print(f"  - Groups: {len(generator.groups)}")
        print(f"  - Rooms: {len(generator.rooms)}")
        print(f"  - Faculty: {len(generator.faculty)}")
        
        # Try generation with detailed logging
        print("\n5. Generation attempt...")
        
        # Generate
        result = generator.generate_timetable(program_id, semester)
        
        print("\n6. Final Result:")
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Schedule entries: {len(result['schedule'])}")
            print(f"Score: {result['score']}")
        else:
            print(f"Error: {result['error']}")
            
    except Exception as e:
        print(f"Error during generation: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== DEBUG COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(detailed_debug())