import asyncio
from app.db.mongodb import connect_to_mongo, db
from bson import ObjectId

async def analyze_constraints():
    """Analyze current constraints and suggest fixes"""
    await connect_to_mongo()
    
    print("=== CONSTRAINT ANALYSIS ===")
    
    # Get courses
    courses_cursor = db.db.courses.find({
        'program_id': ObjectId('68b5c517e73858dcb11d37e4'), 
        'semester': 5
    })
    courses = await courses_cursor.to_list(length=None)
    
    # Get rooms
    rooms_cursor = db.db.rooms.find({})
    rooms = await rooms_cursor.to_list(length=None)
    
    # Get faculty
    faculty_cursor = db.db.faculty.find({})
    faculty = await faculty_cursor.to_list(length=None)
    
    # Calculate total hours needed
    total_theory_hours = sum(c.get('theory_hours', 0) for c in courses)
    total_practical_hours = sum(c.get('practical_hours', 0) for c in courses)
    total_hours = total_theory_hours + total_practical_hours
    
    print(f"Total courses: {len(courses)}")
    print(f"Total theory hours needed: {total_theory_hours}")
    print(f"Total practical hours needed: {total_practical_hours}")
    print(f"Total hours needed: {total_hours}")
    print(f"Available rooms: {len(rooms)}")
    print(f"Available faculty: {len(faculty)}")
    
    # Calculate available time slots
    working_days = 5  # Mon-Fri
    slots_per_day = 6  # Based on 9:00-17:00 with breaks
    total_slots = working_days * slots_per_day
    
    print(f"\nTime slot analysis:")
    print(f"Working days: {working_days}")
    print(f"Slots per day: {slots_per_day}")
    print(f"Total available slots: {total_slots}")
    print(f"Hours needed: {total_hours}")
    print(f"Utilization: {(total_hours/total_slots)*100:.1f}%")
    
    # Check faculty distribution
    faculty_assignments = {}
    for course in courses:
        fac_id = course.get('faculty_id')
        if fac_id:
            if fac_id not in faculty_assignments:
                faculty_assignments[fac_id] = []
            faculty_assignments[fac_id].append({
                'code': course.get('code'),
                'theory_hours': course.get('theory_hours', 0),
                'practical_hours': course.get('practical_hours', 0)
            })
    
    print(f"\nFaculty workload analysis:")
    for fac_id, courses_assigned in faculty_assignments.items():
        total_fac_hours = sum(c['theory_hours'] + c['practical_hours'] for c in courses_assigned)
        print(f"Faculty {fac_id}: {len(courses_assigned)} courses, {total_fac_hours} hours")
        for course in courses_assigned:
            print(f"  - {course['code']}: {course['theory_hours']}h theory, {course['practical_hours']}h practical")

async def redistribute_faculty():
    """Redistribute faculty to reduce conflicts"""
    print("\n=== REDISTRIBUTING FACULTY ===")
    
    # Get all faculty and courses
    faculty_cursor = db.db.faculty.find({})
    faculty = await faculty_cursor.to_list(length=None)
    
    courses_cursor = db.db.courses.find({
        'program_id': ObjectId('68b5c517e73858dcb11d37e4'), 
        'semester': 5
    })
    courses = await courses_cursor.to_list(length=None)
    
    # Separate theory and practical courses
    theory_courses = [c for c in courses if c.get('theory_hours', 0) > 0]
    practical_courses = [c for c in courses if c.get('practical_hours', 0) > 0]
    
    print(f"Theory courses: {len(theory_courses)}")
    print(f"Practical courses: {len(practical_courses)}")
    
    # Assign different faculty to theory and practical courses
    faculty_index = 0
    
    # Assign theory courses
    for course in theory_courses:
        assigned_faculty = faculty[faculty_index % len(faculty)]
        faculty_index += 1
        
        result = await db.db.courses.update_one(
            {'_id': course['_id']},
            {'$set': {'faculty_id': assigned_faculty['_id']}}
        )
        
        print(f"Assigned {assigned_faculty.get('name', 'Unknown')} to theory course {course.get('code')}")
    
    # Assign practical courses (continue with different faculty)
    for course in practical_courses:
        assigned_faculty = faculty[faculty_index % len(faculty)]
        faculty_index += 1
        
        result = await db.db.courses.update_one(
            {'_id': course['_id']},
            {'$set': {'faculty_id': assigned_faculty['_id']}}
        )
        
        print(f"Assigned {assigned_faculty.get('name', 'Unknown')} to practical course {course.get('code')}")

async def create_additional_student_groups():
    """Create additional student groups to reduce room conflicts"""
    print("\n=== CREATING ADDITIONAL STUDENT GROUPS ===")
    
    # Get existing group
    existing_group_cursor = db.db.student_groups.find({
        'program_id': ObjectId('68b5c517e73858dcb11d37e4'),
        'semester': 5
    })
    existing_groups = await existing_group_cursor.to_list(length=None)
    
    if len(existing_groups) < 2:
        # Create a second group
        new_group = {
            'name': 'Group B - Semester 5',
            'program_id': ObjectId('68b5c517e73858dcb11d37e4'),
            'semester': 5,
            'year': 3,
            'section': 'B',
            'size': 25,
            'student_strength': 25,
            'group_type': 'regular',
            'course_ids': [],
            'created_by': 'system',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z'
        }
        
        result = await db.db.student_groups.insert_one(new_group)
        print(f"Created additional student group: {result.inserted_id}")
    else:
        print(f"Already have {len(existing_groups)} groups")

async def main():
    try:
        await analyze_constraints()
        await redistribute_faculty()
        await create_additional_student_groups()
        print("\n=== CONSTRAINT FIXES COMPLETE ===")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())