#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongodb import connect_to_mongo, db
from bson import ObjectId

async def test_data_loading():
    """Test data loading from database"""
    print("Testing data loading...")
    
    # Connect to database
    await connect_to_mongo()
    
    program_id = "68b5c517e73858dcb11d37e4"
    semester = 5
    
    # Load courses
    courses = await db.db.courses.find({
        "program_id": ObjectId(program_id),
        "semester": semester,
        "is_active": True
    }).to_list(length=None)
    print(f"Found {len(courses)} courses")
    
    # Load groups
    groups = await db.db.student_groups.find({
        "program_id": program_id
    }).to_list(length=None)
    print(f"Found {len(groups)} groups")
    
    # Load rooms
    rooms = await db.db.rooms.find({"is_active": True}).to_list(length=None)
    print(f"Found {len(rooms)} rooms")
    
    # Load faculty
    faculty = await db.db.faculty.find({}).to_list(length=None)
    print(f"Found {len(faculty)} faculty")
    
    # Print course details
    print("\nCourse details:")
    for course in courses:
        print(f"  {course.get('code')}: {course.get('name')} - {course.get('hours_per_week')}h/week")
    
    # Write results to file
    with open('test_results.txt', 'w') as f:
        f.write(f"Courses: {len(courses)}\n")
        f.write(f"Groups: {len(groups)}\n")
        f.write(f"Rooms: {len(rooms)}\n")
        f.write(f"Faculty: {len(faculty)}\n")
        f.write("\nCourse details:\n")
        for course in courses:
            f.write(f"  {course.get('code')}: {course.get('name')} - {course.get('hours_per_week')}h/week\n")
    
    print("Results written to test_results.txt")

if __name__ == "__main__":
    asyncio.run(test_data_loading())