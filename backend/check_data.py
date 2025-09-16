#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.mongodb import db, connect_to_mongo
from bson import ObjectId

async def check_data():
    """Check available data for timetable generation"""
    try:
        await connect_to_mongo()
        print("Connected to database")
        
        program_id = "68b5c517e73858dcb11d37e4"  # CSE AI-ML
        
        # Check courses
        courses = await db.db.courses.find({"program_id": ObjectId(program_id)}).to_list(length=None)
        print(f"\nCourses for CSE AI-ML program: {len(courses)}")
        for course in courses[:5]:  # Show first 5
            print(f"- {course.get('code', 'N/A')}: {course.get('name', 'N/A')} ({course.get('credits', 'N/A')} credits)")
        
        # Check faculty
        faculty = await db.db.faculty.find({}).to_list(length=None)
        print(f"\nTotal faculty members: {len(faculty)}")
        for f in faculty[:5]:  # Show first 5
            print(f"- {f.get('name', 'N/A')}: {f.get('department', 'N/A')}")
        
        # Check rooms
        rooms = await db.db.rooms.find({}).to_list(length=None)
        print(f"\nTotal rooms: {len(rooms)}")
        for room in rooms[:5]:  # Show first 5
            print(f"- {room.get('name', 'N/A')}: {room.get('type', 'N/A')} (capacity: {room.get('capacity', 'N/A')})")
        
        # Check student groups
        groups = await db.db.student_groups.find({"program_id": ObjectId(program_id)}).to_list(length=None)
        print(f"\nStudent groups for CSE AI-ML: {len(groups)}")
        for group in groups:
            print(f"- {group.get('name', 'N/A')}: {group.get('size', 'N/A')} students")
            
        await db.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_data())