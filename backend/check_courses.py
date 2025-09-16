import asyncio
from app.db.mongodb import db, connect_to_mongo
from bson import ObjectId

async def check_courses():
    # Initialize database connection
    await connect_to_mongo()
    program_id = '68b5c517e73858dcb11d37e4'
    
    # Check all courses for this program
    courses = await db.db.courses.find({'program_id': ObjectId(program_id)}).to_list(length=None)
    print(f'Found {len(courses)} courses for program {program_id}')
    
    for course in courses[:10]:  # Show first 10
        print(f'Course: {course.get("code", "N/A")} - {course.get("name", "N/A")} - Semester: {course.get("semester", "N/A")} - Active: {course.get("is_active", "N/A")}')
    
    # Check semester 1 specifically
    sem1_courses = await db.db.courses.find({
        'program_id': ObjectId(program_id),
        'semester': 1
    }).to_list(length=None)
    print(f'\nFound {len(sem1_courses)} courses for semester 1')
    
    # Check active semester 1 courses
    active_sem1_courses = await db.db.courses.find({
        'program_id': ObjectId(program_id),
        'semester': 1,
        'is_active': True
    }).to_list(length=None)
    print(f'Found {len(active_sem1_courses)} active courses for semester 1')

if __name__ == '__main__':
    asyncio.run(check_courses())