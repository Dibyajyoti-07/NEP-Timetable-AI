import asyncio
from app.db.mongodb import connect_to_mongo, db
from bson import ObjectId

async def fix_student_groups():
    """Fix student groups to have proper 'size' field"""
    await connect_to_mongo()
    
    print("=== FIXING STUDENT GROUPS ===")
    
    # Get all student groups
    groups_cursor = db.db.student_groups.find({})
    groups = await groups_cursor.to_list(length=None)
    
    print(f"Found {len(groups)} student groups")
    
    for group in groups:
        group_id = group['_id']
        print(f"\nGroup ID: {group_id}")
        print(f"Current fields: {list(group.keys())}")
        
        # Check if group has size field
        if 'size' not in group:
            # Try to get size from student_count or set default
            size = group.get('student_count', 30)  # Default to 30 if no size info
            
            # Update the group
            result = await db.db.student_groups.update_one(
                {'_id': group_id},
                {'$set': {'size': size}}
            )
            
            print(f"  Added 'size' field with value: {size}")
            print(f"  Update result: {result.modified_count} documents modified")
        else:
            print(f"  Already has 'size' field: {group['size']}")

async def check_rooms_and_faculty():
    """Check rooms and faculty data"""
    
    print("\n=== CHECKING ROOMS ===")
    rooms_cursor = db.db.rooms.find({})
    rooms = await rooms_cursor.to_list(length=None)
    
    print(f"Found {len(rooms)} rooms")
    for room in rooms[:3]:  # Show first 3
        print(f"  Room: {room.get('name', 'Unknown')} - Capacity: {room.get('capacity', 'Unknown')}")
    
    print("\n=== CHECKING FACULTY ===")
    faculty_cursor = db.db.faculty.find({})
    faculty = await faculty_cursor.to_list(length=None)
    
    print(f"Found {len(faculty)} faculty members")
    for fac in faculty[:3]:  # Show first 3
        print(f"  Faculty: {fac.get('name', 'Unknown')} - Specialization: {fac.get('specialization', 'Unknown')}")
    
    print("\n=== CHECKING COURSES ===")
    courses_cursor = db.db.courses.find({'program_id': ObjectId('68b5c517e73858dcb11d37e4'), 'semester': 5})
    courses = await courses_cursor.to_list(length=None)
    
    print(f"Found {len(courses)} courses for program 68b5c517e73858dcb11d37e4, semester 5")
    for course in courses:
        print(f"  Course: {course.get('code', 'Unknown')} - {course.get('name', 'Unknown')}")
        print(f"    Theory hours: {course.get('theory_hours', 0)}, Practical hours: {course.get('practical_hours', 0)}")
        print(f"    Faculty: {course.get('faculty_id', 'Not assigned')}")

async def main():
    try:
        await fix_student_groups()
        await check_rooms_and_faculty()
        print("\n=== DATABASE FIXES COMPLETE ===")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())