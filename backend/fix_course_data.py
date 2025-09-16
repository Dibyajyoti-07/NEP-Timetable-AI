import asyncio
from app.db.mongodb import connect_to_mongo, db
from bson import ObjectId

async def fix_course_data():
    """Fix course data by adding proper hours and faculty assignments"""
    await connect_to_mongo()
    
    print("=== FIXING COURSE DATA ===")
    
    # Get all faculty members
    faculty_cursor = db.db.faculty.find({})
    faculty = await faculty_cursor.to_list(length=None)
    faculty_ids = [f['_id'] for f in faculty]
    
    print(f"Available faculty: {len(faculty_ids)}")
    
    # Course data with proper hours and types
    course_updates = {
        'PCCAIML501': {'theory_hours': 4, 'practical_hours': 0, 'type': 'theory'},
        'PCCCS502': {'theory_hours': 3, 'practical_hours': 0, 'type': 'theory'},
        'PCCCS503': {'theory_hours': 3, 'practical_hours': 0, 'type': 'theory'},
        'PCCAIML502': {'theory_hours': 3, 'practical_hours': 0, 'type': 'theory'},
        'PECAIML501A': {'theory_hours': 3, 'practical_hours': 0, 'type': 'theory'},
        'HSMC501': {'theory_hours': 3, 'practical_hours': 0, 'type': 'theory'},
        'PCCCS592': {'theory_hours': 0, 'practical_hours': 3, 'type': 'practical'},
        'PCCCS593': {'theory_hours': 0, 'practical_hours': 3, 'type': 'practical'},
        'PCCAIML592': {'theory_hours': 0, 'practical_hours': 3, 'type': 'practical'}
    }
    
    # Get courses for the specific program and semester
    courses_cursor = db.db.courses.find({
        'program_id': ObjectId('68b5c517e73858dcb11d37e4'), 
        'semester': 5
    })
    courses = await courses_cursor.to_list(length=None)
    
    print(f"Found {len(courses)} courses to update")
    
    faculty_index = 0
    for course in courses:
        course_code = course.get('code', '')
        course_id = course['_id']
        
        print(f"\nUpdating course: {course_code}")
        
        # Get update data for this course
        update_data = course_updates.get(course_code, {
            'theory_hours': 3, 
            'practical_hours': 0, 
            'type': 'theory'
        })
        
        # Assign faculty in round-robin fashion
        assigned_faculty = faculty_ids[faculty_index % len(faculty_ids)]
        faculty_index += 1
        
        # Update the course
        update_fields = {
            'theory_hours': update_data['theory_hours'],
            'practical_hours': update_data['practical_hours'],
            'type': update_data['type'],
            'faculty_id': assigned_faculty
        }
        
        result = await db.db.courses.update_one(
            {'_id': course_id},
            {'$set': update_fields}
        )
        
        print(f"  Theory hours: {update_data['theory_hours']}")
        print(f"  Practical hours: {update_data['practical_hours']}")
        print(f"  Type: {update_data['type']}")
        print(f"  Assigned faculty: {assigned_faculty}")
        print(f"  Update result: {result.modified_count} documents modified")

async def verify_course_data():
    """Verify the updated course data"""
    print("\n=== VERIFYING COURSE DATA ===")
    
    courses_cursor = db.db.courses.find({
        'program_id': ObjectId('68b5c517e73858dcb11d37e4'), 
        'semester': 5
    })
    courses = await courses_cursor.to_list(length=None)
    
    total_theory_hours = 0
    total_practical_hours = 0
    
    for course in courses:
        theory_h = course.get('theory_hours', 0)
        practical_h = course.get('practical_hours', 0)
        total_theory_hours += theory_h
        total_practical_hours += practical_h
        
        print(f"Course {course.get('code', 'Unknown')}: {theory_h}h theory, {practical_h}h practical, Faculty: {course.get('faculty_id', 'None')}")
    
    print(f"\nTotal weekly hours: {total_theory_hours + total_practical_hours}")
    print(f"Theory hours: {total_theory_hours}")
    print(f"Practical hours: {total_practical_hours}")

async def main():
    try:
        await fix_course_data()
        await verify_course_data()
        print("\n=== COURSE DATA FIXES COMPLETE ===")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())