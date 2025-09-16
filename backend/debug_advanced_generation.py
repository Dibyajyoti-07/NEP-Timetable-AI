import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.timetable.advanced_generator import AdvancedTimetableGenerator, SchedulingRules
from app.db.mongodb import db, connect_to_mongo, close_mongo_connection
from bson import ObjectId
import traceback

async def debug_advanced_generation():
    """Debug the advanced timetable generation with detailed error reporting"""
    try:
        print("🔍 Starting Advanced Generation Debug...")
        
        # Connect to database
        await connect_to_mongo()
        print("✅ Connected to MongoDB")
        
        # Test parameters from the frontend error
        program_id = "68b5c517e73858dcb11d37e4"
        semester = 5
        academic_year = "2025-26"
        
        print(f"📋 Testing with: Program ID: {program_id}, Semester: {semester}, Year: {academic_year}")
        
        # Check if program exists
        program = await db.db.programs.find_one({"_id": ObjectId(program_id)})
        if not program:
            print("❌ Program not found!")
            return
        
        print(f"✅ Program found: {program.get('name', 'Unknown')}")
        
        # Check available data
        courses = await db.db.courses.find({"program_id": ObjectId(program_id), "semester": semester}).to_list(None)
        faculty = await db.db.faculty.find({}).to_list(None)
        rooms = await db.db.rooms.find({}).to_list(None)
        student_groups = await db.db.student_groups.find({"program_id": program_id}).to_list(None)
        
        print(f"📚 Available data:")
        print(f"   Courses: {len(courses)}")
        print(f"   Faculty: {len(faculty)}")
        print(f"   Rooms: {len(rooms)}")
        print(f"   Student Groups: {len(student_groups)}")
        
        if len(courses) == 0:
            print("❌ No courses found for this program and semester!")
            return
        
        if len(faculty) == 0:
            print("❌ No faculty found!")
            return
            
        if len(rooms) == 0:
            print("❌ No rooms found!")
            return
            
        if len(student_groups) == 0:
            print("❌ No student groups found!")
            return
        
        # Print detailed data
        print("\n📚 Course Details:")
        for course in courses:
            print(f"   - {course.get('code', 'N/A')}: {course.get('name', 'N/A')} ({course.get('hours_per_week', 0)} hrs/week)")
        
        print("\n👨‍🏫 Faculty Details:")
        for f in faculty:
            print(f"   - {f.get('name', 'N/A')} ({f.get('department', 'N/A')}) - Max: {f.get('max_hours_per_week', 0)} hrs/week")
        
        print("\n🏫 Room Details:")
        for room in rooms:
            print(f"   - {room.get('name', 'N/A')} ({room.get('type', 'N/A')}) - Capacity: {room.get('capacity', 0)}")
        
        print("\n👥 Student Group Details:")
        for group in student_groups:
            print(f"   - {group.get('name', 'N/A')} (Year {group.get('year', 'N/A')}, Strength: {group.get('student_strength', 0)})")
        
        # Create scheduling rules with default values
        rules = SchedulingRules()
        
        print("\n🤖 Creating Advanced Timetable Generator...")
        generator = AdvancedTimetableGenerator(rules)
        
        print("📊 Loading data into generator...")
        await generator.load_from_database(program_id, semester)
        
        print("🚀 Starting timetable generation...")
        result = await generator.generate_timetable()
        
        if result["success"]:
            print(f"✅ Generation successful!")
            print(f"   Timetable ID: {result.get('timetable_id', 'N/A')}")
            print(f"   Score: {result.get('score', 'N/A')}")
            print(f"   Attempts: {result.get('attempts_made', 'N/A')}")
            print(f"   Schedule entries: {len(result.get('schedule', []))}")
        else:
            print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
            if 'details' in result:
                print(f"   Details: {result['details']}")
        
    except Exception as e:
        print(f"❌ Exception during debug: {str(e)}")
        print(f"📋 Full traceback:")
        traceback.print_exc()
    
    finally:
        await close_mongo_connection()
        print("🔌 Disconnected from MongoDB")

if __name__ == "__main__":
    asyncio.run(debug_advanced_generation())